# :coding: utf-8


import sys
import platform
import shotgun_api3


def search_ip(name_val):
    # shotgunapi
    sg = shotgun_api3.Shotgun(
        'site',
        'id',
        'password'
    )
    # 이름 확인
    entity      = 'HumanUser'
    filters     = [
                    [ 'name', 'contains', name_val ],
                    [ 'sg_status_list', 'is', 'act' ]
                ]
    fields      = [ 'id', 'name' ]
    sg_users    = sg.find( entity, filters, fields )

    # ip 검색
    if sg_users == []:
        print( '이름이 없거나, 잘못 입력하셨습니다.' )
    elif len( sg_users ) == 1:
        check_filters    = [ [ 'sg_user', 'is', sg_users ] ]
        check_fields     = [ 'id', 'name', 'description', 'sg_user' ]
        check            = sg.find( 'CustomNonProjectEntity05', check_filters, check_fields )
        if check == []:
            pass
        else:
            print( check[ 0 ][ 'sg_user' ][ 'name' ])
            print( check[ 0 ][ 'description' ] )
    else:
        for i in range( len( sg_users ) ):
            check_filters  = [ [ 'sg_user', 'is', sg_users[i] ] ]
            check_fields   = [ 'id', 'name', 'description', 'sg_user' ]
            check          = sg.find( 'CustomNonProjectEntity05', check_filters, check_fields )
            if check == []:
                pass
            else: 
                print( check[ 0 ][ 'sg_user' ][ 'name' ])
                print( check[ 0 ][ 'description' ])

# 운영체제가 리눅스인 경우에만 실행
if platform.system() == 'Linux':
    name_var = sys.argv[1]
    search_ip(name_var)

