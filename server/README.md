Server Files

All requests from Tree Diagram have been directed to the get_model function in views.py.
(This can be found in /opt/systemsens/service/visualization)

Enabling the get_model function requires that it be defined in urls.py (in the /service folder)

The get_model function works as such:
	- All requests must provide a version code of their model, IMEI, and boolean "tree" flag.
	- get_model will check whether an entry for this IMEI exists, and if it does, whether a model is already being processed
	- Pathways:
		- If no entry exists, creates an entry in the database and starts model creation. (200)
		- If entry exists, and updating flag isn't set
			- and version number of model in database is <= to reported version, start model creation. (200)
			- and version number of model in database is > reported version, send model. (204)
		- If entry exists, and updating flag is set
			- send "wait" to client (202).

Model creation occurs based on "tree" flag:
- If tree is true,
	- Starts thread, generates ARFF file using python script, then calls run_tree.sh
- If tree is false,
	- Starts thread, generates ARFF file using python script, then calls run_model.sh

Differences:
	- run_tree.sh will output a JSON object into the corresponding column in user_models.
	- run_model.sh will generate a .model file that must be attached as a byte stream to the HttpResponse.
