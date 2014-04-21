# Beer Manager API

An implementation of a beer manager application for keeping track of beers, users, beer reviews, and user favorites.
The implementation is using Flask, flask-restful, and deployed to the Google App Engine.
[Flask micro framework](http://flask.pocoo.org).

# Run Locally
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

# Deploy
To deploy the application:

1. Use the [Admin Console](https://appengine.google.com) to create a
   project/app id. (App id and project id are identical)
2. [Deploy the
   application](https://developers.google.com/appengine/docs/python/tools/uploadinganapp) with

   ```
   appcfg.py -A <your-project-id> --oauth2 update .
   ```
3. Congratulations!  Your application is now live at your-app-id.appspot.com

# API Documentation
## General Commands:

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
5. Errors:

   400 - Bad Input

   404 - Object not found

   405 - Not allowed

   429 - Rate limit exceeded (includes allowed_in seconds when action is allowed next)
6. Supported Input:

   The API supports a variety of input including JSON, form, url args, and anything that can be parsed from the request
   as long as the variable name matches the input name

   IE you can add favorites using the following methods:

   URL arguments
   ```
   POST
   /api/v1.0/users/<user id>/favorites?beer_id=<beer id>
   ```
   JSON body
   ```
   POST
   /api/v1.0/users/<user id>/favorites
   BODY
   { "beer_id": <beer id> }
   ```
   JSON Body through favorites
   ```
   POST
   /api/v1.0/favorites
   BODY
   { "user_id": <user id>, "beer_id": <beer id> }
   ```

   The method of input is supported via almost all commands, commands that have multiple ways to post are get are
   documented below


## Beer Commands

beer input:
```
{
    'name': string, [Required, unique]
    'description': string, [Required]
    'ibu': float,
    'calories': float,
    'abv': float,
    'style': float,
    'brewery_location': float,
    'beer_glass_id': int,
}
```

beer object:
```
{
    'name': fields.String,
    'description': fields.String,
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

## User Commands

user input:
```
{
    'user_name': string, [Required]
    'first_name': string, [Required]
    'last_name': string, [Required]
    'password': string [Required]
}
```

user object:
```
{
    'user_name': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
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

## Beer Glasses

beer_glass input:
```
{
    'name': fields.String, [Required]
    'description': fields.String,
    'capacity': fields.Float,
}
```

beer_glass object:
```
{
    'name': fields.String,
    'description': fields.String,
    'capacity': fields.Float,
    'uri': IdUrlField('beer_glass', absolute=True),
}
```

1. Get list of beer glasses:
   /api/v1.0/beer_glasses - GET
   Input: None
   Output: beer_glass array
2. Get specific beer glass:
   /api/v1.0/beer_glasses/<id> - GET
   Input: Beer Glass ID
   Output: beer_glass object
3. Add new beer glass:
   /api/v1.0/beer_glasses - POST
   Input: Required fields passed in with request
   Output: beer_glass object or error
4. Update beer glass:
   /api/v1.0/beer_glasses/<id> - PUT
   Input: Beer Glass ID, Fields that need to be updated
   Output: updated beer_glass object or error
5. Delete beer glass:
   /api/v1.0/beer_glasses/<id> - DELETE
   Input: Beer Glass ID
   Output: deleted beer_glass object and action or error

## Beer Review

beer_review input
```
{
    'user_id': int, [Required]
    'beer_id': int, [Required]
    'aroma': float, [Required]
    'appearance': float, [Required]
    'taste': float, [Required]
    'palate': float, [Required]
    'bottle_style': float, [Required]
    'comments': fields.String,
}
```

beer_review object
```
{
    'user': fields.Nested(user_reference_fields), [Required]
    'beer': fields.Nested(beer_reference_fields), [Required]
    'date_created': fields.DateTime, [auto generated]
    'aroma': fields.Float, [Required]
    'appearance': fields.Float, [Required]
    'taste': fields.Float, [Required]
    'palate': fields.Float, [Required]
    'bottle_style': fields.Float, [Required]
    'overall': fields.Float, [output - calculated]
    'comments': fields.String,
    'uri': IdUrlField('review', absolute=True)
}
```

beer_review_summary object
```
{
    'count': fields.Integer,
    'aroma': fields.Float,
    'appearance': fields.Float,
    'taste': fields.Float,
    'palate': fields.Float,
    'bottle_style': fields.Float,
    'overall': fields.Float,
    'comments': fields.String,
    'beer': fields.Nested(beer_reference_fields),
}
```

To get summaries of reviews use type argument to specify summary

IE:

/api/v1.0/beer_reviews?type=summary

1. Get all beer reviews:
   /api/v1.0/beer_reviews - GET
   Input: None
   Output: beer_review array or beer_review_summary array
2. Get specific beer review:
   /api/v1.0/beer_reviews/<id> - GET
   Input: Beer Review ID
   Output: beer_review object
3. Get beer review for a beer:
   /api/v1.0/beers/<id>/reviews - GET
   Input: Beer ID
   Output: beer_review array or beer_review_summary object
4. Get reviews for specific user:
   /api/v1.0/users/<id>/reviews - GET
   Input: Beer ID
   Output: beer_review array
5. Add beer review:
   /api/v1.0/beer_reviews - POST
   /api/v1.0/beers/<id>/reviews - POST
   Input: Beer ID and beer_review input object
   Output: beer_review object

## Favorites

favorites input
```
{
    'beer_id': int, [Required]
    'user_id': int, [Required]
}
```

favorites object
```
{
    'beer': fields.Nested(beer_summary_fields),
    'user': fields.Nested(user_summary_fields),
    'uri': IdUrlField('favorite', absolute=True),
}
```

1. Get all favorites:
   /api/v1.0/favorites - GET
   Input: None
   Output: favorites array
2. Get specific favorite:
   /api/v1.0/favorites/<id> - Get
   Input: Favorite ID
   Output: favorite object
3. Get favorites for a user:
   /api/v1.0/users/<id>/favorites - GET
   Input: User ID
   Output: favorite array
4. Add favorite beer:
   /api/v1.0/favorites - POST
   /api/v1.0/users/<id>/favorites - POST
   Input: User ID and Beer ID
   Output: favorite object
5. Delete favorite by id:
   /api/v1.0/favorites/<id> - DELETE
   Input: Favorite ID
   Output: deleted favorite object and action: deleted
6. Delete favorite beer for user:
   /api/v1.0/users/<id>/favorites - DELETE
   Input: User ID and Beer ID
   Output: deleted favorite object and action: deleted
