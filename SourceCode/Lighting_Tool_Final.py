# -*- coding:utf-8 -*-
import os
import re

import shiboken2
import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI

from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
    QListWidget, QComboBox, QDialog, QAbstractItemView

root_path = "Root to Repository "
sequence_path = f'{root_path}\asset_final\published\sequence'


def getMayaWindow():
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken2.wrapInstance(int(ptr), QWidget)


class MyWindow(QDialog):
    def __init__(self, parent=None):
        """UI design"""
        parent = parent or getMayaWindow()
        super(MyWindow, self).__init__(parent)
        self.resize(600, 450)
        self.setWindowTitle('Lighting Tool')

        self.episode_combo_box = QComboBox()
        if os.path.exists(sequence_path):
            self.populate_episode_combo_box(
                sequence_path,
                self.episode_combo_box
                )
        self.episode_combo_box.currentIndexChanged.connect(self.episode_change)
        self.shot_combo_box = QComboBox()
        self.shot_combo_box.currentIndexChanged.connect(self.shot_change)

        self.listView_charcache = QListWidget()  # create character ache list
        self.listView_charcache.setSelectionMode(
            QAbstractItemView.ExtendedSelection
            )  
        self.listView_propcache = QListWidget()  # create prop cache list
        self.listView_propcache.setSelectionMode(
            QAbstractItemView.ExtendedSelection
            )  
        self.listView_camcache = QListWidget()  #  create camera cache list
        self.listView_camcache.setSelectionMode(
            QAbstractItemView.ExtendedSelection
            )  

        self.import_camera_bt = QPushButton('import_camera')  #import camera assets button
        self.import_select_character_bt = QPushButton(
            'import_select_character')  #import character cache button
        self.import_select_prop_bt = QPushButton(
            'import_select_prop')  #import prop cache button
        self.import_allcache_bt = QPushButton('import_all')  #import all assets button
        self.check_allcache_bt = QPushButton('Check_version')  #version check button
        self.update_allcache_bt = QPushButton('Update_version')  #update button

        self.signal_connect()

        main_layout = QVBoxLayout()
        load_shot_layout = QHBoxLayout()
        cachelist_layout = QHBoxLayout()
        select_layout = QHBoxLayout()
        import_layout = QHBoxLayout()
        update_layout = QHBoxLayout()

        load_shot_layout.addWidget(self.episode_combo_box)
        load_shot_layout.addWidget(self.shot_combo_box)

        cachelist_layout.addWidget(self.listView_charcache)
        cachelist_layout.addWidget(self.listView_propcache)
        cachelist_layout.addWidget(self.listView_camcache)

        select_layout.addWidget(self.import_select_character_bt)
        select_layout.addWidget(self.import_select_prop_bt)
        select_layout.addWidget(self.import_camera_bt)

        import_layout.addWidget(self.import_allcache_bt)

        update_layout.addWidget(self.check_allcache_bt)
        update_layout.addWidget(self.update_allcache_bt)

        main_layout.addLayout(load_shot_layout)
        main_layout.addLayout(cachelist_layout)
        main_layout.addLayout(select_layout)
        main_layout.addLayout(import_layout)
        main_layout.addLayout(update_layout)

        self.setLayout(main_layout)

    def signal_connect(self):
        """
        to connect each function and sign
        """
        self.import_camera_bt.clicked.connect(self.import_camera)
        self.import_select_character_bt.clicked.connect(
            self.import_select_character)
        self.import_select_prop_bt.clicked.connect(self.import_select_prop)
        self.import_allcache_bt.clicked.connect(self.import_all_cache)
        self.check_allcache_bt.clicked.connect(self.check_cache_version)
        self.update_allcache_bt.clicked.connect(self.update_cache_version)

    def show_warning_dialog(
            self, warningstr,
            high_version=[],
            low_version=[],
            update=False):

        if high_version and low_version:
            updatestr = 'Need updated version:\n'
            if update:
                updatestr = 'Version updated successfully:\n'
            for index, value in enumerate(low_version):
                updatestr += '{0}>>>{1}\n'.format(value, high_version[index])
            result_window = cmds.confirmDialog(
                title='prompt',
                message=updatestr,
                button=['Sure']
            )

        if warningstr:
            result_window = cmds.confirmDialog(
                title='warning',
                message=warningstr,
                button=['Sure']
            )
        return result_window

    def populate_episode_combo_box(self, sequence_path, combo_box):

        episode_name_list = [
            episode_name for episode_name in os.listdir(
                sequence_path) if os.path.isdir(
                    os.path.join(sequence_path, episode_name))]
        combo_box.addItem('')
        combo_box.addItems(episode_name_list)

    def clearcharlist(self):
        """clear character cache list"""
        self.listView_charcache.clear()

    def clearproplist(self):
        """clear prop cache list"""
        self.listView_propcache.clear()

    def clearcamlist(self):
        """clear camera cache list"""
        self.listView_camcache.clear()

    def episode_change(self):

        episode = self.episode_combo_box.currentText()
        episode_path = os.path.join(sequence_path, episode)
        self.shot_combo_box.clear()
        for shotname in os.listdir(episode_path):
            shotname_path = os.path.join(episode_path, shotname)
            if os.path.isdir(shotname_path):
                self.shot_combo_box.addItem(shotname)

    def shot_change(self):

        self.clearcharlist()
        self.clearproplist()
        self.clearcamlist()
        cache_path = self.get_cache_path()
        cache_list = self.get_cache_file(cache_path)
        if cache_list:
            self.set_cache_list(cache_list)

    def get_cache_path(self):
        sc_name = self.episode_combo_box.currentText()
        shot_name = self.shot_combo_box.currentText()
        cache_path = os.path.join(sequence_path, sc_name, shot_name)
        cache_path = os.path.join(cache_path, 'cache')
        return cache_path

    def get_cache_file(self, cachepath):
        cache_list = []
        if os.path.exists(cachepath):
            cache_type = ['.abc', '.fbx']
            cache_list = self.get_latest_cache_file(cachepath, cache_type)
        return cache_list

    def get_latest_cache_file(self, target_path, cache_type):

        file_dict = {}
        for filename in os.listdir(target_path):
            for file_extension in cache_type:
                if filename.endswith(file_extension):
                    file_name, version = filename.split('_v')
                    if file_name not in file_dict:
                        file_dict[file_name] = []
                    file_dict[file_name].append(
                        (filename, int(version.split('.')[0])))
        latest_files = []
        for file_name, file_list in file_dict.items():
            sorted_files = sorted(file_list, key=lambda x: x[1])
            latest_file = sorted_files[-1][0]
            latest_files.append(latest_file)
        return latest_files

    def get_cam_cachepath(self, cachepath):
        """
        Get the path of the camera cache file.
        """
        cam_name = next(
            (os.path.join(cachepath, cache_name) for cache_name in os.listdir(
                cachepath) if '_cam' in cache_name), '')
        return cam_name

    def set_cache_list(self, cache_list):
        for cache_name in cache_list:
            if '_char' in cache_name:
                self.listView_charcache.addItem(cache_name)
            if '_prop' in cache_name:
                self.listView_propcache.addItem(cache_name)
            if '_cam' in cache_name:
                self.listView_camcache.addItem(cache_name)

    def import_func(self, cache_path):
        """Import cache files."""
        namesp = os.path.splitext(
            os.path.basename(cache_path))[0].split('_v')[0]
        cache_options = ';readAnimData=1;useAsAnimationCache=1'
        cmds.file(
            cache_path,
            reference=True,
            options=cache_options,
            lockReference=False,
            loadReferenceDepth='all',
            namespace=namesp,
            returnNewNodes=False
        )

    def import_camera(self):
        cachepath = self.get_cache_path()
        cam_name = self.listView_camcache.item(0).text()
        if cam_name:
            cam_cache_path = os.path.join(cachepath, cam_name)
            self.import_func(cam_cache_path)
        else:
            warningstr = 'Camera cache not found'
            self.show_warning_dialog(
                warningstr=warningstr,
                high_version=[],
                low_version=[])

    def import_select_character(self):
        cache_path = self.get_cache_path()
        if self.listView_charcache.selectedItems():
            for charcachename in self.listView_charcache.selectedItems():
                cache_file_path = os.path.join(
                    cache_path,
                    charcachename.text()
                    )
                self.import_func(cache_file_path)
        else:
            warningstr = 'The character to be imported is not selected'
            self.show_warning_dialog(
                warningstr=warningstr,
                high_version=[],
                low_version=[])

    def import_select_prop(self):
        cache_path = self.get_cache_path()
        if self.listView_propcache.selectedItems():
            for propcachename in self.listView_propcache.selectedItems():
                cache_file_path = os.path.join(
                    cache_path, propcachename.text())
                self.import_func(cache_file_path)
        else:
            warningstr = 'The props to be imported are not selected'
            self.show_warning_dialog(
                warningstr=warningstr,
                high_version=[],
                low_version=[])

    def import_all_cache(self):
        """
        import all cache files
        """
        cache_path = self.get_cache_path()
        cache_list = self.get_cache_file(cache_path)
        for cache_file in cache_list:
            cache_file_path = os.path.join(cache_path, cache_file)
            self.import_func(cache_file_path)

    def compare_versions(self, cache_list, ref_list):
        """
        Compare version numbers of cached files
        """
        higher_versions = []
        replace_versions = []
        lower_versions = []
        unique_files = []
        for file1 in cache_list:
            match1 = re.match(r'(.*)_v(\d+)\.', file1)
            if match1:
                name1, version1 = match1.groups()
                matching_files = [
                    file2 for file2 in ref_list if file2.startswith(name1)]
                if matching_files:
                    match2 = re.match(r'.*_v(\d+)\.', matching_files[0])
                    if match2:
                        version2 = match2.group(1)
                        if int(version1) > int(version2):
                            higher_versions.append(file1)
                            replace_versions.append(matching_files[0])
                        elif int(version1) < int(version2):
                            lower_versions.append(file1)
                else:
                    unique_files.append(file1)
        return higher_versions, replace_versions, lower_versions, unique_files

    def get_cache_version_diff(self):
        """By taking the cache file path and reference file list by using compare_versions."""
        cache_path = self.get_cache_path()
        cache_list = self.get_cache_file(cache_path)
        ref_list = [
            os.path.basename(
                ref_path) for ref_path in cmds.file(q=True, r=True)]
        return self.compare_versions(cache_list, ref_list)

    def check_cache_version(self):
        """If a replacement version exists, show a warning dialog."""
        higher, replaces, lower, unique = self.get_cache_version_diff()
        if replaces:
            self.show_warning_dialog(
                warningstr='',
                high_version=higher,
                low_version=replaces)

    def update_cache_version(self):
        """
        Update cached file version
        """
        higher, replaces, lower, unique = self.get_cache_version_diff()
        cache_path = self.get_cache_path()
        if replaces:
            for index, value in enumerate(replaces):
                refpath = os.path.join(cache_path, value)
                refnode = cmds.referenceQuery(refpath, rfn=True)
                newrefpath = os.path.join(cache_path, higher[index])
                cmds.file(
                    newrefpath,
                    loadReference=refnode,
                    loadReferenceDepth='all',
                    options='v=0')
            self.show_warning_dialog(
                warningstr='',
                high_version=higher,
                low_version=replaces,
                update=True)


def main():
    global win
    win = MyWindow()
    win.show()


if __name__ == '__main__':
    main()
