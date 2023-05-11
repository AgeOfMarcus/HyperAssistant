from langchain.tools import BaseTool
from langchain.tools.base import Field, Any
import requests

class WeatherTool(BaseTool):
    name = "GetWeather"
    description = (
        "Get's the weather near the User."
        "Useful for checking weather near User."
        "Does not accept any arguments."
        "Returns a string containing the weather."
    )

    user: Any = Field(default=None)

    def _run(self, *args, **kwargs):
        if (loc := self.user.last_location):
            resp = requests.get('https://wttr.in/{}?format=3'.format(
                f'{loc["lat"]},{loc["lon"]}'
            ))
            return resp.text
        else:
            return 'Error: User has not set location. Please instruct the user to use the `/location` command.'
        
    async def _arun(self, *args, **kwargs):
        return self._run()