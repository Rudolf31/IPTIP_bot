import logging

from database.controllers.employee_controller import EmployeeController

logger = logging.getLogger(__name__)


class EmployeeService:
    """
    EmployeeService is responsible for
    employee related actions.
    """

    async def getEmployeeList() -> list:
        employees = await EmployeeController.getEmployees()
        return [f"""{e.full_name} - {e.birthday}""" for e in employees]