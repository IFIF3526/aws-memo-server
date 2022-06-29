from http import HTTPStatus
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
import mysql.connector

class MemoListResource(Resource) :
    
    # 클라이언트로부터 /recipes/~3~ 이런식으로 바뀌는 숫자로 경로를 처리하므로 변수로 처리해준다.
    def get(self, memo_id) :
        
        # DB에서, memo_id 에 들어있는 값에 해당되는
        # 데이터를 select 해온다.
        
        try :
            connection = get_connection()

            query ='''select *
                    from memo
                    where id = %s;'''
            record = (memo_id, )

            #select 문은, dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            # select 문은, 아래 함수를 이용해서, 데이터를 가져온다.
            result_list = cursor.fetchall()

            print(result_list)
            
            # 중요, DB에서 가져온 timestamp는
            # 파이썬의 datetime 으로 자동 변환된다.
            # 문제는, 이 데이터를 json으로 바로 보낼 수 없으므로
            # 문자열로 바꾼뒤 저장하여 보낸다.

            i = 0
            for record in result_list :
                result_list[i]['date'] = record['date'].isoformat()
                result_list[i]['created_at'] = record['created_at'].isoformat()
                result_list[i]['updated_at'] = record['updated_at'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 503
        
        return {"result" : "success", "info" : result_list[0]}, 200



    # 데이터를 업데이트하는 API들은 put 함수를 사용한다.
    @jwt_required()
    def put(self, memo_id) :

        # body에서 전달된 데이터를 처리
        data = request.get_json()

        user_id = get_jwt_identity()

        # DB업데이트 실행코드
        try :
            # 데이터 업데이트
            # 1. DB에 연결
            connection = get_connection()

            ### 먼저 memo_id 에 들어있는 user_id가
            ### 이 사람인지 먼저 확인한다.  

            query = '''select user_id
                    from memo
                    where id = %s;'''

            record = (memo_id, )

            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()
            print(1)

            memo = result_list[0]

            if memo['user_id'] != user_id :
                cursor.close()
                connection.close()
                return {'error' : '다른 이용자의 메모를 수정할 수 없습니다.'}, 401 

            # 2. 쿼리문 만들기
            query = '''update memo
                    set title = %s,
                    date = %s,
                    description = %s
                    where id = %s;'''
            # MySQL Workbench에서 먼저 실행하여보고 가져온다.
            # query = '''update memo
            #         set title = %s,
            #         date = %s,
            #         description = %s,
            #         where id = %s;'''
            # 무엇이 문제인지 알겠는가?
            # desc ... 부분의 마지막에 SQL문법상 맞지않는 ,가 들어가 있어서 syntax에러가 발생했다...
            # 꼭 먼저 테스트를 해보고 입력할것...

            record = (data['title'], data['date'], data['description'], memo_id)
            
            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            print(memo_id)

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record)
            print(2)

            # 5. 커넥션을 커밋해줘야 한다 => DB에 영구적으로 반영하라는 뜻
            connection.commit()
                
            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 503

        return {'result' : 'success'}, 200


    # 삭제하는 delete 함수
    def delete(self, memo_id) :

        try :
            # 데이터 삭제
            # 1. DB에 연결
            connection = get_connection()

            # 2. 쿼리문 만들기
            query = '''delete from memo
                    where id = %s;'''

            record = (memo_id, )
            
            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record)

            # 5. 커넥션을 커밋해줘야 한다 => DB에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 503

        return {'result' : 'success'}, 200

# CRUD