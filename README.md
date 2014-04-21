## Beer Manager API

An implementation of a beer manager application for keeping track of beers, users, beer reviews, and user favorites.
The implementation is using Flask, flask-restful, and deployed to the Google App Engine.
[Flask micro framework](http://flask.pocoo.org).

## Run Locally
1. Install the [App Engine Python SDK](https://developers.google.com/appengine/downloads).
See the README file for directions. You'll need python 2.7 and [pip 1.4 or later](http://www.pip-installer.org/en/latest/installing.html) installed too.

2. Clone this repo with

   ```
   git clone https://github.com/pwojt/beer_app_414.git
   ```
3. Install dependencies in the project's lib directory.
   Note: App Engine can only import libraries from inside your project directory.

   ```
   pip install -r requirements.txt -t lib
   ```
4. Run this project locally from the command line:

   ```
   dev_appserver.py .
   ```

Visit the application [http://localhost:8080](http://localhost:8080)

## Deploy
To deploy the application:

1. Use the [Admin Console](https://appengine.google.com) to create a
   project/app id. (App id and project id are identical)
2. [Deploy the
   application](https://developers.google.com/appengine/docs/python/tools/uploadinganapp) with

   ```
   appcfg.py -A <your-project-id> --oauth2 update .
   ```
3. Congratulations!  Your application is now live at your-app-id.appspot.com

## API Documentation
# General Commands:

1. Command format:
   /api/v1.0/<object>[/id[/sub_object]]
   object - specifies the object you want to act on (beers, beer_glasses, beer_reviews, users, favorites)
   id - (optional) the object ID you want to act on
   sub_object - (optional) if ID is specified, gets the sub object, ie all user reviews would be: /api/v1.0/user/<id>/reviews
2. Authentication:
   The api supports basic authentication using user name and password.
   When the application first runs, it creates a default admin user to allow access to the system.
   Default admin credentials:
   user_name: admin
   password: beer_app1
3. Sorting:
   To sort lists returned from get specify the sort parameter via url arguments.
   sort=<field name> - (optional) sort on specified field name, returns 400 result if sort field is not available
   order=<asc|desc> - (optional) if sort is selected, order descending or ascending (default) sort order
4. Return:
   All data is returned as a JSON object.
   Each object returns the uri reference back to the object
   When posting or putting an object, a single entry with the object put is returned
   When getting an object, the single object is returned
   ```
   {
      "beer": { <beer object> }
   }
   ```
   When getting multiple object an array of the object is returned
   ```
   {
      "beers": [<beer object>`1, ... <beer object>`n]
   }
   ```
   When deleting an object, the object is returned along with the action: deleted.

# Beer Commands

beer object:
```
{
    'name': fields.String, [Required]
    'description': fields.String, [Required]
    'ibu': fields.Float,
    'calories': fields.Float,
    'abv': fields.Float,
    'style': fields.String,
    'brewery_location': fields.String,
    'beer_glass': ReferenceUrlField('beer_glass', absolute=True),
    'uri': IdUrlField('beer', absolute=True),
}
```

1. Get list of beers:
   /api/v1.0/beers - GET
   Input: None
   Output: beers array
2. Get specific beer:
   /api/v1.0/beers/<id> - GET
   Input: Beer ID
   Output: beer object
3. Add new beer:
   /api/v1.0/beers - POST
   Input: Required fields passed in with request
   Output: beer object or error
4. Update beer:
   /api/v1.0/beers/<id> - PUT
   Input: Beer ID, Fields that need to be updated
   Output: updated beer object or error
5. Delete beer:
   /api/v1.0/beers/<id> - DELETE
   Input: Beer ID
   Output: deleted beer object and action or error

# User Commands

user object:
```
{
    'user_name': fields.String, [Required]
    'first_name': fields.String, [Required]
    'last_name': fields.String, [Required]
    'password': fields.String, [Input Only/Required]
    'last_beer_add_date': fields.DateTime,
    'uri': IdUrlField('user', absolute=True),
}
```

1. Get list of users:
   /api/v1.0/users - GET
   Input: None
   Output: user array
2. Get specific user:
   /api/v1.0/users/<id> - GET
   Input: User ID
   Output: user object
3. Add new user:
   /api/v1.0/user - POST
   Input: Required fields passed in with request
   Output: user object or error
4. Update user:
   /api/v1.0/users/<id> - PUT
   Input: User ID, Fields that need to be updated
   Output: updated user object or error
5. Delete user:
   /api/v1.0/users/<id> - DELETE
   Input: User ID
   Output: deleted user object and action or error
