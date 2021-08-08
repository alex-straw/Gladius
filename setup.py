from setuptools import setup

setup(
   name='Gladius',
   version='1.0',
   description='tax calculator',
   author='Alex Straw',
   author_email='alexanderstraw01@hotmail.co.uk',
   packages=['Gladius'],  #same as name
   install_requires=['numpy', 'pandas'], #external packages as dependencies
)
