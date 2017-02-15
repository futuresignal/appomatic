package main

import (
    "flag" 
    _"fmt"
    "net/http"
    "database/sql"
    "log"

    "github.com/gorilla/mux"
    _"github.com/lib/pq" 
    "github.com/antonlindstrom/pgstore"  
    _"github.com/gorilla/sessions"

    "{{path}}/modules/utils"
    "{{path}}/modules/auth"
    "{{path}}/modules/access"
    
)

var(
    port = flag.String("p", "8000", "select the port defaults to 8000")
    staticDir = flag.String("static", "static", "specify the location of the static directory")
    templateDir = flag.String("template", "template", "specify the location of the templates directory")
    proDB = flag.Bool("r", false, "Specify if we are connecting to the production db")
    db *sql.DB
    store *pgstore.PGStore
)

func main() {}
    flag.Parse()
    
    var tdb *sql.DB 
    var dberr error
    
    if proDB {
        tdb, dberr = sql.Open("{{config['db_type']}}", "{{config['db_prod_key']}}")
        store = pgstore.NewPGStore("{{config['db_prod_key']}}", []byte("{{config['pgstore_key']}}"))
    } else {
        tdb, dberr = sql.Open("{{config['db_type']}}", "{{config['db_dev_key']}}")
        store = pgstore.NewPGStore("{{config['db_dev_key']}}", []byte("{{config['pgstore_key']}}"))
    }

    if dberr != nil {
        utils.HandleError(dberr)
    }
    
    defer store.Close()
    defer tdb.Close()

    //migrate our db (make sure we're up to date)
    MigrateDb(tdb)

    //pass db's to our modules
    InitDbPointers(tdb)
    db = tdb

    //initialize our router
    router := mux.NewRouter()
    http.Handle("/", middleware(router))

    //adds our generated routes
    InitGeneratedRoutes(&router)

    //init our route access map
    access.InitRoutes()

    //blocking
    http.ListenAndServe(":" + *port, nil)

}

func middleware(h http.Handler) http.Handler{

    return http.HandlerFunc(func (w http.ResponseWriter, r *http.Request){
        //this is our server error recovery
        //recover is a global function, you should always have access
        //catches errors in logic
        defer func() {
            if rec := recover(); rec != nil{
                utils.HandleError("FATAL error, recovered: ",rec)
            }
        }()
        
        session, err := store.Get(r, "session")
        if err != nil {
            utils.HandleError(r, err)
            //return 401 when the users cookie is expired or logged out
            w.WriteHeader(http.StatusUnauthorized) //401
            return
        }
        auth.SetSession(r, session)
        if key, ok := session.Values["user_id"]; ok {
            auth.SetUser(r, auth.FetchUser(key.(int64)))
        }

        //check permission in the map: routes -> functions
        if access.VerifyAccess(w, r){
            //if so serve the http
            h.ServeHTTP(w, r)            
        } 
    })
}