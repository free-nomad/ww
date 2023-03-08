# :coding: utf-8


import os
import platform
import subprocess

import shotgun_api3


def update_ip():
    # 사번
    user = os.environ[ 'USER' ]

    # IP 주소
    ip_cmd  = "hostname -I"
    ip_proc = subprocess.Popen( ip_cmd , shell = True, stdout = subprocess.PIPE ).communicate()
    ip      = ip_proc[0].replace('\n', '').split(' ')
    ip      = ip[0]

    # shotgunapi
    sg = shotgun_api3.Shotgun(
        'site',
        'id',
        'password'
    )

    # 사번 존재 유무 확인
    text_search  = sg.text_search( user, {"CustomNonProjectEntity05": []} )

    if text_search['matches'] == []:
        # 사번 활용을 통한 이름 찾기
        entity      = 'HumanUser'
        filters     = [
                            [ 'sg_ww_id', 'is', user],
                            [ 'sg_status_list', 'is', 'act' ]
                    ]
        fields      = [ 'id', 'name' ]
        sg_users    = sg.find_one( entity, filters, fields )

        # 사번 / 이름 / ip 생성
        create_data = {
                            "code"        : user,
                            "sg_user"     : sg_users,
                            "description" : ip
                    }
        create      = sg.create( 'CustomNonProjectEntity05', create_data )

    else:
        # 사번 활용을 통한 이름 찾기
        entity   = 'HumanUser'
        filters  = [
                                [ 'sg_ww_id', 'is', user],
                                [ 'sg_status_list', 'is', 'act' ]
                ]
        fields   = [ 'id', 'name' ]
        sg_users = sg.find_one( entity, filters, fields )

        # ip 수정
        update_filters  = [
                                [ 'code', 'is', user],
                                [ 'sg_user', 'is', sg_users ]
                        ]
        update_fields   = [ 'id', 'name' ]
        update_id       = sg.find_one( 'CustomNonProjectEntity05', update_filters, update_fields )

        update_data     = { 'description': ip }
        update          = sg.update( 'CustomNonProjectEntity05', update_id['id'], update_data )


# 운영체제가 리눅스인 경우에만 실행
if platform.system() == 'Linux':
    update_ip()