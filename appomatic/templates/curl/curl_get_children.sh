
#get GetAll_{{rel['table']}}_By_{{submodule}}
curl -v -u username:password -i -X GET http://localhost:3000/api/{{config['api_version']}}/GetAll_{{rel['table']}}_By_{{submodule}}/{id:[0-9]+}/