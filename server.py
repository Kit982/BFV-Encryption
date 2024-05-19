from fastapi import FastAPI, Body, status
from fastapi.responses import JSONResponse

from BFV import *
from poly import *
from helper import *
from client import *

# условная база данных выполняемых задач
tasks = []


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


def compute(x, y, expression=None):
    # todo добавить вычисление своей функции
    ct = Evaluator.HomomorphicAddition(x, y)
    return ct
    # return x + y


# отправка данных для вычисления
@app.post("/api/compute")
def start_computing(data=Body()):
    # парсинг данных
    task_id = data["id"]
    x_value = data["x"]
    y_value = data["y"]

    tasks.append(task_id)

    # todo добавить извлечение функции для вычисления

    # todo добавить своё вычислеие
    result = compute(x_value, y_value)

    tasks.remove(task_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "id": f"{task_id}",
            "result": f"{result}"
        }
    )