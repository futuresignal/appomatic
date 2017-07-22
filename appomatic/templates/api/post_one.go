
//
// PostOne_{{table_name}} Profides our create endpoint
// Params: 
// Returns: 
//
func PostOne_{{table_name}}(w *utils.ResponseWrapper, r *http.Request){
	var db_struct {{struct_name}}

	err := utils.DecodePost(&db_struct, w, r)
	if err != nil {
		w.SendResponse(400, map[string]string{"error":"Unable to decode post"}, err)
		return
	}

	err = CreateOne_{{table_name}}(&db_struct)
	if err != nil {
		w.SendResponse(500, map[string]string{"error":"Internal Error"}, err)
		return
	}

	w.SendResponse(201, db_struct, err)
	

}

