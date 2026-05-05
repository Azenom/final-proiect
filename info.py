'''
connections :
    create db
    
employees :
    add :
        bulk : import csv file
        update db
        singular : in web app
        update db
    edit :
        singular : in web app
        update db

assets :
    add : 
        bulk : import csv file
        update db
        singular : in web app
        update db
    edit :
        singular : in web app
        update db

assigments : ( logic : Employee ← assignment → Asset)
    add : 
        singular : in web app
    update db
    edit :
        singular : in web app
    update db

display : 
    employees : 
        import from db
        display in web app
    assets in use: 
        import from db
        display in web app
    assets free :
        import from db
        display in web app
    assets broken/repair : 
        import from db
        display in web app
    assignments :
        import from db 
        display in web app

exports :
    separate csv : employees, assets, assigments



'''