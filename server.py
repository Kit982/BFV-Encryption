from fastapi import FastAPI, Body, status
from fastapi.responses import JSONResponse, FileResponse

from BFV import *
from poly import *
from helper import *
# from client import *
import jsonpickle

# условная база данных выполняемых задач
tasks = []

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

qnp = [w_table, wv_table, psi_table, psiv_table]
Evaluator = BFV(n, q, t, mu, sigma, qnp)

def find_task(id):
    for task_id in tasks:
        if task_id == id:
            return True
    return False


app = FastAPI()


# получение статуса задачи
@app.get("/api/task/{id}")
def get_task(id):
    # получаем пользователя по id
    task_computing = find_task(id)

    if task_computing is True:
        # если задача выполняется
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Задача выполняется"}
        )

    # если задачи нет
    return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Задача не найдена"}
        )


def compute_sub(x, y, expression=None):
    ct_sub = Evaluator.HomomorphicSubtraction(x, y)
    return ct_sub


def compute_summ(x, y, expression=None):
    ct_summ = Evaluator.HomomorphicAddition(x, y)
    return ct_summ


def compute_mult(x, y, expression=None):
    ct_mult = Evaluator.HomomorphicMultiplication(x, y)
    ct_mult = Evaluator.RelinearizationV2(ct_mult)
    return ct_mult


# отправка данных для вычисления
@app.post("/api/compute")
def start_computing(data=Body()):
    # парсинг данных
    task_id = data["id"]
    x_value = data["x"]
    y_value = data["y"]
    op = data["operation"]

    tasks.append(task_id)

    pol_1 = jsonpickle.decode(x_value)
    pol_2 = jsonpickle.decode(y_value)

    # todo добавить своё вычислеие
    if ord(op) == 45:
        result = compute_sub(pol_1, pol_2)
    elif ord(op) == 43:
        result = compute_summ(pol_1, pol_2)
    elif ord(op) == 42:
        result = compute_mult(pol_1, pol_2)
    else:
        print("Incorrect operation")
        exit(11)

    result_1 = jsonpickle.encode(result)

    tasks.remove(task_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "id": f"{task_id}",
            "result": f"{result_1}"
        }
    )
