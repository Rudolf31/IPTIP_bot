from database.application_context import AppContext
from database.application_context import Employee


class EmployeeController():
    """
    EmployeeController for database actions
    related to user.
    """
    async def addEmployee(employee) -> Employee:
        """
        Addition of a new employee.

        employee - must be a new Employee object.
        """
        async with AppContext() as database:
            with database.atomic():

                new_employee = Employee.create(
                    full_name=employee.full_name,
                    birthday=employee.birthday,
                    tg_id=employee.tg_id)

                new_employee.save()
                return new_employee

    async def getEmployeeById(id) -> Employee:
        """
        Returns the Employee object from the database that
        matches the given id.

        id - id of Employee.
        """
        async with AppContext() as database:
            with database.atomic():

                return Employee.get_or_none(Employee.id == id)

    async def getEmployeeByTgId(tg_id) -> Employee:
        """
        Returns the Employee object from the database that
        matches the given Telegram user id.

        id - id of the Telegram user.
        """
        async with AppContext() as database:
            with database.atomic():

                return Employee.get_or_none(Employee.tg_id == tg_id)

    async def getEmployees() -> list:
        """
        Returns all employees from the database.
        """
        async with AppContext() as database:
            with database.atomic():

                return list(Employee.select())

    async def deleteEmployee(id) -> bool:
        """
        Deletes the employee that matches the employee id from
        the database. Returns true on success.

        id - id of Employee.
        """
        async with AppContext() as database:
            with database.atomic():

                employee = Employee.get(Employee.id == id)
                employee.delete_instance()
                return True

    async def updateEmployee(employee) -> bool:
        """
        Updates the employee that matches the employee id from
        the database. Returns true on success.

        id - id of Employee.
        """
        async with AppContext() as database:
            with database.atomic():

                employee.save()
                return True
