import logging

from database.controllers.employee_controller import EmployeeController

logger = logging.getLogger(__name__)


class EmployeeService:
    """
    EmployeeService is responsible for
    employee related actions.
    """

    async def getEmployeeList() -> list:
        """
        Returns all employees from the database.
        """
        try:
            employees = await EmployeeController.getEmployees()
            return [f"""{e.full_name} - {e.birthday}""" for e in employees]
        except Exception as e:
            logger.exception(f"Failed to get employee list: {e}")
            return ["Not found"]