
#post {{submodule}}
curl -v -i -H "Content-Type: application/json" -X POST -d '{{json}}' http://localhost:3000/api/{{config['api_version']}}/{{submodule}}/
#post {{submodule}} with credentials
curl -v -u username:password -i -H "Content-Type: application/json" -X POST -d '{{json}}' http://localhost:3000/api/{{config['api_version']}}/{{submodule}}/