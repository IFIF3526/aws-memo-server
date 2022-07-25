from passlib.hash import pbkdf2_sha256

# 원문 비밀번호를, 암호화 하는 함수
def hash_password(original_password) :
    salt = 'yh*hello12'
    password = original_password + salt
    password = pbkdf2_sha256.hash(password)
    return password

# hash는 단방향 암호화다.
# 랜덤과 비슷하다.

# 비밀번호가 맞는지 확인하는 함수 , True / False를 리턴한다.
def check_password(original_password, hashed_password) :
    salt = 'yh*hello12'
    check = pbkdf2_sha256.verify(original_password + salt, hashed_password)
    return check