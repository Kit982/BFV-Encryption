from BFV import *
from poly import *
from helper import *
import jsonpickle


import sys
import uuid

import requests


# Parameter generation (pre-defined or generate parameters)
PD = 0 # 0: generate -- 1: pre-defined

if PD == 0:
    # Select one of the parameter sets below
    t = 16;   n, q, psi = 1024 , 132120577         , 73993                # log(q) = 27
    # t = 256;  n, q, psi = 2048 , 137438691329      , 22157790             # log(q) = 37
    # t = 1024; n, q, psi = 4096 , 288230376135196673, 60193018759093       # log(q) = 58

    # other necessary parameters
    psiv= modinv(psi,q)
    w   = pow(psi,2,q)
    wv  = modinv(w,q)
else:
    # Enter proper parameters below
    t, n, logq = 16, 1024, 27
    # t, n, logq = 256, 2048, 37
    # t, n, logq = 1024, 4096, 58

    # other necessary parameters (based on n and log(q) determine other parameter)
    q,psi,psiv,w,wv = ParamGen(n,logq)

# Determine mu, sigma (for discrete gaussian distribution)
mu    = 0
sigma = 0.5 * 3.2

# Determine T, p (for relinearization and galois keys) based on noise analysis
T = 256
p = q**3 + 1

# Generate polynomial arithmetic tables
w_table    = [1]*n
wv_table   = [1]*n
psi_table  = [1]*n
psiv_table = [1]*n
for i in range(1,n):
    w_table[i]    = ((w_table[i-1]   *w)    % q)
    wv_table[i]   = ((wv_table[i-1]  *wv)   % q)
    psi_table[i]  = ((psi_table[i-1] *psi)  % q)
    psiv_table[i] = ((psiv_table[i-1]*psiv) % q)

qnp = [w_table,wv_table,psi_table,psiv_table]

# Generate BFV evaluator
Evaluator = BFV(n, q, t, mu, sigma, qnp)

# Generate Keys
Evaluator.SecretKeyGen()
Evaluator.PublicKeyGen()
Evaluator.EvalKeyGenV1(T)
Evaluator.EvalKeyGenV2(p)


# адрес сервера
# localhost - локальная машина
# 8000 - порт по умолчанию fastapi
API_SERVER_URL = "http://localhost:8000/api"


def generate_id() -> str:
    # Случайный UUID
    return str(uuid.uuid4())


def start():
    # вот начало клиентской функции

    while True:
        # ввод целых чисел
        x = int(input("Enter int value x: "))
        y = int(input("Enter int value y: "))
        operat = str(input("Enter operation: "))

        # генерация id задачи
        task_id = generate_id()

        m1 = Evaluator.IntEncode(x)
        m2 = Evaluator.IntEncode(y)

        ct1 = Evaluator.Encryption(m1)
        ct2 = Evaluator.Encryption(m2)

        ct_1 = jsonpickle.encode(ct1)
        ct_2 = jsonpickle.encode(ct2)
        print(type(operat))

        # создание запроса
        request_structure = {
            "id": task_id,
            "x": ct_1,
            "y": ct_2,
            "operation": operat
        }

        # отправка запроса
        response = requests.post(f"{API_SERVER_URL}/compute", json=request_structure)

        # ожидание ответа сервера
        server_response = response.json()

        # todo вставить расшифрование x и y
        result_poly = jsonpickle.decode(server_response['result'])
        mt = Evaluator.Decryption(result_poly)

        nr = Evaluator.IntDecode(mt)

        print(f"Ответ для задачи {server_response['id']}")
        print(f"{x} {operat} {y} = {nr}")


if __name__ == '__main__':
    start()
    sys.exit(0)
