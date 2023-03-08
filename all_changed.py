# :coding: utf-8

import os
import sys
import subprocess

import shotgun_api3

import tractor.api.author as author

from PyQt4.QtGui import *
from PyQt4.QtCore import *

# Python2
sys.path.append(
        "rez-env path" 
)

# AttributeError: 'module' object has no attribute 'setdefaultencoding'
reload(sys)
sys.setdefaultencoding('utf8')

BODY = '''# :coding: utf-8
import shotgun_api3
def create_and_upload(
                project, shot_code, content, version_name,
                thumb_file_path, filmstrip_file_path, mp4_file_path, webm_file_path
    ):
    # shotgunapi
    sg = shotgun_api3.Shotgun(
            'site',
            login= 'id',
            password= 'password'
    )
    project_id = sg.find_one( 'Project', [['name','is', project]] )
    fitelrs_one = [ 
                ['project', 'is', project_id],
                ['code', 'is', shot_code] 
    ]
    shot = sg.find_one('Shot', fitelrs_one)
    filters_two = [ 
                ['project', 'is', project_id],
                ['entity', 'is',shot],
                ['content', 'is', content] 
    ]
    task = sg.find_one('Task', filters_two)

    data = dict()
    data['project'] = project_id
    data['code']    = version_name
    data['entity']  = shot
    data['sg_task'] = task

    create_version = sg.create('Version', data)
    filters_three = [ 
                ['sg_task', 'is', task],
                ['code', 'is', version_name]
        ]
    version_id = sg.find_one('Version', filters_three)
    thumb_nail_upload = sg.upload_thumbnail( 
                                                'Version', version_id['id'], thumb_file_path
                                            )
    montage_upload    = sg.upload_filmstrip_thumbnail( 'Version', 
                                        version_id['id'], filmstrip_file_path)
    mp4_upload        =  sg.upload( 'Version', version_id['id'], 
                                        mp4_file_path, 'sg_uploaded_movie_mp4')
    webm_upload       = sg.upload( 'Version', version_id['id'], 
                                        webm_file_path, 'sg_uploaded_movie_webm')

create_and_upload('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')
'''



class MyWindow( QMainWindow ):
    def __init__( self ):
        QMainWindow.__init__( self )
        # 윈도우 특성 설정
        self.setWindowTitle('Packager') 
        self.resize( 400, 200 )
        self.statusBar().showMessage( 'ks' )
        
        # shotgunapi
        self.sg = shotgun_api3.Shotgun(
                'site',
                login='id',
                password='password'
        )

        # 파일 경로 찾기 / 파일 경로 입력 / show list / shot list / task list / submit 버튼 / cancel 버튼
        file_path_search_btn = QPushButton( '....' )
        self.file_path_edt   = QLineEdit()
        self.show_list_cb   = QComboBox()
        self.shot_list_cb   = QComboBox()
        self.task_cb = QComboBox()
        submit_btn = QPushButton( 'Submit' )
        cancel_btn = QPushButton( 'Cancel' )

        # 첫 번째 줄 - Horizontally
        line_edt_lay = QHBoxLayout()
        line_edt_lay.addWidget( self.file_path_edt )
        line_edt_lay.addWidget( file_path_search_btn )

        # 두 번째 줄
        cb_lay = QHBoxLayout()
        cb_lay.addWidget( self.show_list_cb )
        cb_lay.addWidget( self.shot_list_cb  )
        cb_lay.addWidget( self.task_cb  )

        # 세 번째 줄
        btn_lay = QHBoxLayout()
        btn_lay.addWidget( submit_btn )
        btn_lay.addWidget( cancel_btn )

        # 수직 결합 - Vertically
        main_lay = QVBoxLayout()
        main_lay.addLayout( line_edt_lay )
        main_lay.addLayout( cb_lay )
        main_lay.addLayout( btn_lay )
        
        # 공백
        sp = QSpacerItem( 10, 50 )
        main_lay.addSpacerItem( sp )

        # QWidget - 베이스 클래스 -> 이 세줄이 없으면 위의 위젯들이 출력되지 않는다.
        main_widget = QWidget()
        main_widget.setLayout( main_lay )
        self.setCentralWidget( main_widget )

        # 클릭할 때의 이벤트
        submit_btn.clicked.connect( self.file_submit )
        file_path_search_btn.clicked.connect( self.file_path_search_clicked )
        cancel_btn.clicked.connect( QCoreApplication.instance().quit )

        self.show_items()

        # 윈도우 화면에 표시
        self.show()
    
    def file_path_search_clicked( self ):
        file_log = QFileDialog.getExistingDirectory( self )   
        self.file_path_edt.setText( file_log )

    def show_items( self ):
        # 'Active', 'RND' 상태 찾기
        project_fields = [ 'id' , 'name' ]
        project = self.sg.find( 
                                    'Project', 
                                    [
                                        ['sg_status', 'in', [ 'RND','Active'] ]
                                    ], 
                                    project_fields
                                )
    
        # show list
        show_name_list = [ x[ 'name' ].decode( 'utf-8' ) for x in project]
        show_name_list.sort()
        self.show_list_cb.addItem( 'show list' )
        self.shot_list_cb.addItem( 'shot list' )
        self.task_cb.addItem( 'task list' )
        self.show_list_cb.addItems( show_name_list )
        self.show_list_cb.currentIndexChanged.connect( self.shot_items )

    def shot_items( self ):

        # 테스트
        self.show_list_cb.blockSignals( True )

        if str( self.show_list_cb.currentText() ) == 'show list': 
            self.shot_list_cb.clear()
            self.task_cb.clear()
            self.shot_list_cb.insertItem( 0, 'shot list' )
            self.task_cb.insertItem( 0, 'task list' )

            print('shot_items -- if')

        else:
            self.shot_list_cb.clear()
            self.task_cb.clear()
            self.shot_list_cb.insertItem( 0, 'shot list' )
            self.task_cb.insertItem( 0, 'task list' )
            # shot code 
            shot_fields = ['id', 'code']

            shot = self.sg.find(
                        'Shot', 
                        [
                            ['project.Project.name', 'is', str( self.show_list_cb.currentText() )]
                        ], 
                        shot_fields
                    )

            # shot list
            shot_name_list = [ y['code'].decode('utf-8') for y in shot]
            shot_name_list.sort()
            self.shot_list_cb.addItems( shot_name_list )
            self.shot_list_cb.currentIndexChanged.connect( self.task_items )

            print('shot_items -- else')
        
    def task_items( self ):
        # 테스트
        self.shot_list_cb.blockSignals( True )

        self.task_cb.clear()
        self.task_cb.insertItem(0, 'task list')
        if str( self.show_list_cb.currentText() ) != 'show list':
            if str( self.shot_list_cb.currentText() ) != '':
                task_fields = [ 'id', 'content' ]
                task = self.sg.find(
                            'Task', 
                            [
                                ['project.Project.name', 'is', str( self.show_list_cb.currentText() )],
                                ['entity.Shot.code', 'is', str( self.shot_list_cb.currentText() )]
                            ], 
                            task_fields
                        )

                task_name_list = [ z['content'].decode('utf-8') for z in task]
                task_name_list.sort()
                self.task_cb.addItems( task_name_list )

                print('task_items -- in')
        
        print('task_items -- out')

    def file_submit(self):
        if str(  self.show_list_cb.currentText()) != 'show list' and \
            str( self.shot_list_cb.currentText()) != 'shot list' and \
            str( self.task_cb.currentText()) != 'task list' and \
            str( self.file_path_edt.text())  != None:

            # ex. path
            input_folder  = str( self.file_path_edt.text() )
            # ex. path
            parent_folder = os.path.dirname( input_folder )

            file_name_list     = sorted( os.listdir( input_folder ) )
            file_header        = file_name_list[0].split('.')[0]
            start_number       = file_name_list[0].split('.')[1]
            filename_extension = file_name_list[0].split('.')[2]

            '''
            filename_extension = os.path.splitext(file_name_list[0] )[1]
            '.exr'
            os.path.dirname()
            os.path.isdir()
            os.path.isfile()
            os.path.exists()
            os.path.splitext()
            os.path.basename()
            os.makedirs()
            os.sep

            '''


            # ex. path
            tractor_folder = parent_folder + os.sep + file_header + '_tractor'
            # ex. path
            dest_file      = input_folder + os.sep + file_header

            # 업로드할 파일 폴더
            cmd = "mkdir {0}".format( tractor_folder )
            proc = subprocess.Popen( cmd , shell = True, stdout=subprocess.PIPE ).communicate()

            ffmpeg = "rez-env ffmpeg -- ffmpeg -y"
            number_range = "%04d"

            # thumbnail 
            thumbnail_cmd  = "{0} -i {1}.{2}.{3} ".format( 
                                            ffmpeg, dest_file, 
                                            start_number, filename_extension
                                            )
            thumbnail_cmd += " -f image2 {0}/{1}_thumbnail.jpg".format( 
                                                                tractor_folder,file_header 
                                                                )

            # jpg 폴더
            jpg_folder_cmd = "mkdir {0}/{1}_jpg_folder".format( tractor_folder, file_header )

            # x -> jpg
            convert_cmd = "{0} -start_number {1} -i {2}.{3}.{4}".format(
                                                            ffmpeg, start_number, dest_file, 
                                                            number_range, filename_extension
                                                            )
            convert_cmd += "  {0}/{1}_jpg_folder/{1}.{2}.jpg".format(
                                                            tractor_folder, 
                                                            file_header, number_range
                                                            )
                                                    
            # montage
            montage = "montage"
            thumb_ext = "jpg"
            frame_width = "240"
            quality = "90"

            montage_cmd  = "{0} {1}/{2}_jpg_folder/{2}.*.{3} -geometry {4}x+0+0 ".format( 
                                                            montage, tractor_folder, file_header, 
                                                            thumb_ext, frame_width 
                                                            )
            montage_cmd += "-tile x1 -format jpeg -quality {0} {1}/{2}_filmstrip.jpg".format( 
                                                            quality, tractor_folder, 
                                                            file_header 
                                                            )

            # mp4
            mp4_ext_trc = " -apply_trc iec61966_2_1 -start_number "

            mp4_vcodec = " -vcodec libx264 -pix_fmt yuv420p -preset veryslow -crf 18 "
            mp4_vcodec +=  ' -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2"' 
            mp4_vcodec += ' -x264-params '
            mp4_vcodec += ' "colorprim=smpte170m:transfer=smpte170m:colormatrix=smpte170m" '

            mp4_cmd  = "{0} {1} {2} -i {3}.{4}.{5} ".format( 
                                                            ffmpeg, mp4_ext_trc, start_number, 
                                                            dest_file, number_range, 
                                                            filename_extension
                                                            )
            mp4_cmd += "{0} -f mp4 {1}/{2}.mp4".format( mp4_vcodec, tractor_folder, file_header )

            # webm
            webm_ext_trc = " -apply_trc iec61966_2_1 -start_number "

            webm_vcodec = " -pix_fmt yuv420p -vcodec libvpx -vf 'scale=trunc((a*oh)/2)*2:720'  "
            webm_vcodec += " -g 30 -b:v 2000k -quality realtime -cpu-used 0 -qmin 10 -qmax 42 "
            webm_cmd  = "{0} {1} {2} -i {3}.{4}.{5} ".format( 
                                                            ffmpeg, webm_ext_trc, start_number, 
                                                            dest_file, number_range, 
                                                            filename_extension
                                                            )
            webm_cmd += "{0} -f webm {1}/{2}.webm".format( 
                                                            webm_vcodec, tractor_folder,  
                                                            file_header
                                                            )

            # create_py
            self.create_py_cmd(tractor_folder, file_header)

            # tractor function
            self.tractor_upload(
                                            thumbnail_cmd, jpg_folder_cmd, convert_cmd, 
                                            montage_cmd, mp4_cmd, webm_cmd, tractor_folder, 
                                            file_header
                                            )
        
        else:
            QMessageBox.about(self,'알림'.decode('utf-8'),
                                            '파일 경로 혹은 리스트 목록을 모두 선택해주세요.'.decode('utf-8'))


    def create_py_cmd( self, py_path, header ):
        thumbnail_path = py_path +  os.sep + header + "_thumbnail.jpg"
        montage_path   = py_path +  os.sep + header + "_filmstrip.jpg"
        mp4_path       = py_path +  os.sep + header + ".mp4"
        webm_path      = py_path +  os.sep + header + ".webm"

        version_name = header

        with open( '{0}/{1}_to_sg.py'.format(py_path, header), 'w' ) as f:
            f.write( BODY.format(
                                            str(self.show_list_cb.currentText()), str(self.shot_list_cb.currentText()), 
                                            str(self.task_cb.currentText()), version_name, thumbnail_path, 
                                            montage_path, mp4_path, webm_path
                                            )
                        )

    def tractor_upload(self, thumbnail_cmd, jpg_folder_cmd, convert_cmd, montage_cmd, 
                                    mp4_cmd, webm_cmd, server_folder_path, file_header):
        job = author.Job() # <class 'tractor.api.author.base.Job'>
        job.service = "Linux64"
        job.priority = 100  #우선순위 높을수록 우선순위가 올라감
        job.title = 'RND TEST'  #제목은 HTML 규칙
        job.projects = ['RND'] #project column에 등록 되는 value

        task7 = author.Task( title   = 'thumbnail' )
        cmd7  = author.Command( argv = thumbnail_cmd )
        task7.addCommand( cmd7 )

        task6 = author.Task( title   = 'jpg_folder' )
        cmd6  = author.Command( argv = jpg_folder_cmd )
        task6.addCommand( cmd6 )

        task5 = author.Task( title   = 'convert' )
        cmd5  = author.Command( argv =  convert_cmd )
        task5.addCommand( cmd5 )

        task4 = author.Task( title   = 'montage' )
        cmd4  = author.Command( argv =  montage_cmd )
        task4.addCommand( cmd4 )

        task3 = author.Task( title = 'mp4' )
        # 이스케이프 문자 자동 삽입 문제 해결 코드
        cmd3  = author.Command( argv = mp4_cmd.replace('\"', '') ) 
        task3.addCommand( cmd3 )

        task2 = author.Task( title = 'webm' )
        # 큰 따옴표(") 자동 삽입 문제 해결 코드 
        cmd2  = author.Command( argv = webm_cmd.replace("'", '') ) 
        task2.addCommand( cmd2 )

        exec_py = 'rez-env shotgunapi3 -- python {0}/{1}_to_sg.py'.format(
                                                                    server_folder_path, file_header
                                                                    ) 
        task = author.Task( title   = 'python file' )
        cmd  = author.Command( argv = exec_py )
        task.addCommand( cmd )

        task6.addChild( task7 )
        task5.addChild( task6 )
        task4.addChild( task5 )
        task3.addChild( task4 )
        task2.addChild( task3 )
        task.addChild( task2 )
        job.addChild( task )

        author.setEngineClientParam(
            hostname = 'ip',
            port     = 'port',
            user     = 'w10271',
            debug    = True
        )

        job.spool()
        author.closeEngineClient()


def main():
    app = QApplication(sys.argv)
    ex = MyWindow()
    # ex.show() -> 생성자 말고 여기에서 show() 
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()