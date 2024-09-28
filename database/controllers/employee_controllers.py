from database.application_context import AppContext
from database.application_context import Employee


class EmployeeController():
    async def addEmployee(employee) -> Employee:

        async with AppContext() as database:
            with database.atomic():
                
                new_employee = Employee.create(full_name=employee.full_name, birthday=employee.birthday, tg_id=employee.tg_id)
                new_employee.save()
                return new_employee


    async def getEmployeeById(id) -> Employee:

        async with AppContext() as database:
            with database.atomic():

                return Employee.get(Employee.id == id)

    async def getEmployeeByTgId(tg_id) -> Employee:

        async with AppContext() as database:
            with database.atomic():

                return Employee.get(Employee.tg_id == tg_id)


    async def deleteEmployee(id) -> bool:

        async with AppContext() as database:
            with database.atomic():

                employee = Employee.get(Employee.id == id)
                employee.delete_instance()
                return True


    async def updateEmployee(employee) -> bool:

        async with AppContext() as database:
            with database.atomic():

                employee.save()
                return True