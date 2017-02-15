
#get {{submodule}}
curl -v -i -X GET http://localhost:3000/api/{{config['api_version']}}/{{submodule}}/{id:[0-9]+}/
#get {{submodule}} with credentials
curl -v -u username:password -i -X GET http://localhost:3000/api/{{config['api_version']}}/{{submodule}}/{id:[0-9]+}/