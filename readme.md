**ISSUE**: 1
**Login and Registration**: In order to facilitate end users' testing of the API and eliminate the need for them to copy and paste their username and password, the data on the openapi spec page must match for both registration and login.
1. We need to Authorize then
2. Click on try it out in register and also in login
3. Then we can find the Error
4. we have to create the issue and then created the branch
5. we need change the code in app/schemas/the user_schemas.py according to the username and password
6. Then we need to run the "docker compose exec fastapi pytest tests/test_api/test_users_api.py::test_delete_user_does_not_exist"
7. And also "docker compose exec fastapi alembic upgrade head"
8. After running this two commands then we need to refresh the local/docs then we can find the out as same username and password in the both register and login


**ISSUE**: 2
**NULL VALUES**: 
1. We need to Authorize then
2. Click on try it out in GET
3. Then we can see the issue that is:
       - full_name=Null,
       - bio=Null,
       - profile_picture_url=Null,
4. In github Repository we have to create the issue and then created the branch
5. Now I have added the below lines in the app/routers/user_routes.py:
       - full_name=user.full_name,
       - bio=user.bio,
       - profile_picture_url=user.profile_picture_url,
6. Then we need to run the "docker compose exec fastapi pytest tests/test_api/test_users_api.py::test_delete_user_does_not_exist"
7. And also "docker compose exec fastapi alembic upgrade head"
8. After running this two commands then we need to refresh the local/docs then we can see there is no Null values


**ISSUE**: 3
**URL**:
1. We need to Authorize then
2. Click on try it out in PUT
3. Then we can see that the URL is not updating. that is the issue in the issue 3
4. In github Repository we have to create the issue and then created the branch
5. We have to change the http url to string in the app/schemas/user_schemas.py so that the issue get updated in the localhost/doc
6. After changing the code we need to refresh the localhost/doc so that it gets updated in PUT.


**WHAT I HAVE LEARNED FROM THIS ASSIGNMENT IS**:
