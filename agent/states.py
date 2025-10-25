from pydantic import BaseModel, Field

class File(BaseModel):
  path : str = Field(description="The file path where the file should be created, e.g. 'src/App.js'")
  purpose : str = Field(description="A brief description of the purpose of the file, e.g. 'Main application component', 'Data processing Module',etc.")

class Plan(BaseModel):
  name : str = Field(description="The name of the app to be built")
  description : str = Field(description="A oneline despription of the app to be built, e.g. 'A web application for managing personal finances'")
  techstack : str = Field(description="The tech stack to be used for the app, e.g. 'React', 'Python', 'Javascript', 'Flask', etc.")
  features : list[str] = Field(description="A list of features to be implemented in the app, e.g. 'User authentication', 'Data visualization', etc.")
  files : list[File] = Field(description="A list of files to be created, each with a 'path' and 'purpose'")