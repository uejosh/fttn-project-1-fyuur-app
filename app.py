#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
# from models import *
from models import db, Venue, Show, Artist
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm  
from forms import *
from flask import current_app
from flask_migrate import Migrate
from config import *
import sys
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://joshman:@localhost:5432/fyyr'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
db = SQLAlchemy(app)
logging.basicConfig(filename='error.log', level=logging.INFO)

migrate = Migrate(app, db)


# TODO(done): connect to a local postgresql database see config.py
 
#----------------------------------------------------------------------------#
# Models(done). see models.py
#----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@ app.route('/venues')
def venues():
    data = []
    venue_list = Venue.query.order_by('city').all()
    location_genre = db.session.query(Venue).distinct(Venue.city).all()
    for i in range(len(location_genre)):
        content = []
        city = location_genre[i].city
        state = location_genre[i].state
        for a in range(len(venue_list)):
            if city == venue_list[a].city and state == venue_list[a].state:
                print(venue_list[a].city)
                detail = {"id": venue_list[a].id, "name": venue_list[a].name}
                content.append(detail)
                venue_data = {
                    "city": venue_list[a].city,
                    "state": venue_list[a].state,
                    "venues": content}
        data.append(venue_data)
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    research_input = request.form.get('search_term', '')
    search_venue = db.session.query(Venue).filter(Venue.name.ilike(
        '%{}%'.format(research_input))).all()
    now_time = datetime.datetime.today()
    data = []
    for i in search_venue:
        coming_shows = []
        venue_info = {}
        search_result = db.session.query(Venue, Show).join(Show).filter(
            Show.venue_id == Venue.id).filter(Show.venue_id == i.id).all()
        venue_info['id'] = i.id
        venue_info['name'] = i.name
        for x in search_result:
            if x.Show.start_time > now_time:
                coming_shows.append(str(x.Show.start_time))
        venue_info['future_shows'] = len(coming_shows)
        data.append(venue_info)
    response = {
        "count": len(search_venue),
        "data": data
    }
    return render_template('pages/search_venues.html',results=response, search_term=research_input)

@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    now_time = datetime.datetime.now()
    venue_info = db.session.query(Venue).filter(
        Venue.id == venue_id).one_or_none()
    shows = db.session.query(
        Show,
        Artist,
        Venue).join(Artist).join(Venue).filter(
        Show.venue_id == Venue.id).filter(
            Show.artist_id == Artist.id).filter(
                Show.venue_id == venue_id).all()
    # past_shows_query = db.session.query(Show, Venue).join(Venue).filter(
    # Show.artist_id == artist_id).filter(Show.start_time >
    # datetime.now()).all()
    show_coming_data = []
    show_past_data = []
    for i in shows:
        if i.Show.start_time <= now_time:
            performed_artist = {
                'artist_id': i.Artist.id,
                'artist_name': i.Artist.name,
                'artist_image_link': i. Artist.image_link,
                'start_time': str(i.Show.start_time)}
            show_past_data.append(performed_artist)
        else:
            going_artist = {
                'artist_id': i.Artist.id,
                'artist_name': i.Artist.name,
                'artist_image_link': i. Artist.image_link,
                'start_time': str(i.Show.start_time)
            }
            show_coming_data.append(going_artist)
    data = {
        'id': venue_info.id,
        'name': venue_info.name,
        'address': venue_info.address,
        'genres': venue_info.genres,
        'city': venue_info.city,
        'phone': venue_info.phone,
        'website': venue_info.website_link,
        'facebook_link': venue_info.facebook_link,
        'seeking_talent': venue_info.seeking_talent,
        'seeking_description': venue_info.seeking_talent_description,
        'image_link': venue_info.image_link,
        'past_shows': show_past_data,
        'past_shows_count': len(show_past_data),
        'upcoming_shows': show_coming_data,
        'upcoming_shows_count': len(show_coming_data),
    }

    return render_template('pages/show_venue.html', venue=data)
#  Create Venue
#  ----------------------------------------------------------------

#@app.route('/venues/create', methods=['GET'])
#def create_venue_form():
#  form = VenueForm()
#  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  form.validate_on_submit()
  return render_template('forms/new_venue.html', form=form)  

@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
 # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form, meta={'csrf': False})
    if form.venue_validate():
        try:
            venue_name = form.name.data
            venue_city = form.city.data
            venue_state = form.state.data
            venue_address = form.address.data
            venue_phone = form.phone.data
            venue_image_link = form.image_link.data
            venue_genres = form.genres.data
            venue_facebook_link = form.facebook_link.data
            venue_website_link = form.website_link.data
            venue_seeking_talent = form.seeking_talent.data
            venue_talent_description = form.seeking_description.data
            venue_details = Venue(
                name=venue_name,
                address=venue_address,
                city=venue_city,
                state=venue_state,
                phone=venue_phone,
                genres=venue_genres,
                facebook_link=venue_facebook_link,
                image_link=venue_image_link,
                website_link=venue_website_link,
                seeking_talent=venue_seeking_talent,
                seeking_talent_description=venue_talent_description)
            db.session.add(venue_details)
            db.session.commit()
 # on successful db insert, flash success
            flash('Venue ' + form.name.data + ' was successfully listed!')
        except BaseException:
            db.session.rollback()
            logging.error("Error occurred ")
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))
        flash('An error occurred.' +
              form.name.data + ' could not be listed.')
        abort(404)
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')



@app.route('/venues/<int:venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
# TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        print(venue)
        db.session.delete(venue)
        db.session.commit()
        flash('The venue has been removed!')
        print("All clear!")
    except BaseException:
        db.session.rollback()
        logging.error("Catch error/s ")
        abort(500)
    finally:
        db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@ app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
    data = []
    artist_list = Artist.query.order_by('id').all()
    for i in artist_list:
        collection = {}
        collection['id'] = i.id
        collection['name'] = i.name
        data.append(collection)
    return render_template('pages/artists.html', artists=data)

@ app.route('/artists/search', methods=['POST'])
def search_artists():
    research_input = request.form.get('search_term', '')
    search_artist = db.session.query(Artist).filter(
        Artist.name.ilike('%{}%'.format(research_input))).all()
    now_time = datetime.datetime.today()
    data = []
    for i in search_artist:
        coming_shows = []
        artist_info = {}
        search_result = db.session.query(Artist, Show).join(Show).filter(
            Show.artist_id == Artist.id).filter(Show.artist_id == i.id).all()
        artist_info['id'] = i.id
        artist_info['name'] = i.name
        for x in search_result:
            if x.Show.start_time > now_time:
                coming_shows.append(str(x.Show.start_time))
        artist_info['future_shows'] = len(coming_shows)
        data.append(artist_info)
    response = {
        "count": len(search_artist),
        "data": data
    }
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=research_input)

@ app.route('/artists/<int:artist_id>', methods=['GET'])
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id 
    now_time = datetime.datetime.now()
    try:
        artist_info = Artist.query.filter(Artist.id == artist_id).one_or_none()
        shows = db.session.query(
            Show,
            Artist,
            Venue).join(Artist).join(Venue).filter(
            Show.artist_id == Artist.id).filter(
            Show.venue_id == Venue.id).filter(
                Show.artist_id == artist_id).all()
        show_past_data = []
        show_data = []
        for i in shows:
            print(str(i.Show.start_time))
            show_coming_venue = {}
            show_past_venue = {}
            if i.Show.start_time > now_time:
                show_coming_venue['venue_id'] = i.Venue.id
                show_coming_venue['venue_name'] = i.Venue.name
                show_coming_venue['venue_image_link'] = i.Venue.image_link
                show_coming_venue['start_time'] = str(i.Show.start_time)
                show_data.append(show_coming_venue)
                # shows_info
            else:
                show_past_venue['venue_id'] = i.Venue.id
                show_past_venue['venue_name'] = i.Venue.name
                show_past_venue['venue_image_link'] = i.Venue.image_link
                show_past_venue['start_time'] = str(i.Show.start_time)
                show_past_data.append(show_past_venue)

        data = {
            'id': artist_info.id,
            'name': artist_info.name,
            'genres': artist_info.genres,
            'city': artist_info.city,
            'phone': artist_info.phone,
            'website': artist_info.website_link,
            'facebook_link': artist_info.facebook_link,
            'seeking_venue': artist_info.seeking_venue,
            'seeking_description': artist_info.seeking_venue_description,
            'image_link': artist_info.image_link,
            'past_shows': show_past_data,
            'past_shows_count': len(show_past_data),
            'upcoming_shows': show_data,
            'upcoming_shows_count': len(show_data),

        }
    except BaseException:
        logging.error("Error occired " + str())
        abort(404)
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist_detail = Artist.query.filter(Artist.id == artist_id).one_or_none()
    form = ArtistForm(obj=artist_detail)
# TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html',form=form,artist=artist_detail)

@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    try:
        data = Artist.query.filter(Artist.id == artist_id).one_or_none()
        form = ArtistForm(request.form, meta={'csrf': False})
        if form.artist_validate():
            data.name = form.name.data
            data.city = form.city.data
            data.state = form.state.data
            data.phone = form.phone.data
            data.genres = form.genres.data
            data.facebook_link = form.facebook_link.data
            data.image_link = form.image_link.data
            data.website_link = form.website_link.data
            data.seeking_venue = form.seeking_venue.data
            data.seeking_venue_description = form.seeking_description.data
            db.session.commit()
            db.session.close()
            flash('Artist ' + form.name.data + ' was successfully listed!')
        else:
            message = []
            for field, err in form.errors.items():
                message.append(field + ' ' + '|'.join(err))
            flash('Errors ' + str(message))
    except BaseException:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              form.name.data + ' could not be listed.')
        logging.error("Error occired " + str())
        abort(404)
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue_detail = Venue.query.filter(Venue.id == venue_id).one_or_none()
    form = VenueForm(obj=venue_detail)
 # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html',form=form,venue=venue_detail)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.first_or_404(venue_id)
    form = VenueForm(request.form, meta={'csrf': False})
    if form.venue_validate():
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.image_link = form.image_link.data
            venue.genres = form.genres.data
            venue.facebook_link = form.facebook_link.data
            venue.website_link = form.website_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.talent_description = form.seeking_description.data
            db.session.commit()
            flash('Venue ' + form.name.data + ' was successfully listed!')
        except BaseException:
            db.session.rollback()
            logging.error("Error occurred ")
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))
        abort(404)
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form, meta={'csrf': False})
    if form.artist_validate():
        try:
            artist_name = form.name.data
            artist_city = form.city.data
            artist_state = form.state.data
            artist_phone = form.phone.data
            artist_genres = form.genres.data
            artist_facebook_link = form.facebook_link.data
            artist_image_link = form.image_link.data
            artist_website_link = form.website_link.data
            artist_seeking_venue = form.seeking_venue.data
            artist_seeking_description = form.seeking_description.data
            data = Artist(
                name=artist_name,
                city=artist_city,
                state=artist_state,
                phone=artist_phone,
                genres=artist_genres,
                facebook_link=artist_facebook_link,
                image_link=artist_image_link,
                website_link=artist_website_link,
                seeking_venue=artist_seeking_venue,
                seeking_venue_description=artist_seeking_description)
            db.session.add(data)
            db.session.commit()
  # on successful db insert, flash success
            flash('Artist ' + form.name.data + ' was successfully listed!')
        except BaseException:
            db.session.rollback()
            logging.error("Error occired ")
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))
        flash('An error occurred. Artist ' +
              form.name.data + ' could not be listed.')
        abort(404)
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
    data = []
    show_info = db.session.query(
        Venue.id,
        Venue.name,
        Artist.id,
        Artist.name,
        Artist.image_link,
        Show.start_time).select_from(Show).join(Artist).join(Venue).order_by(
        Show.start_time).all()
    for i in range(len(show_info)):
        show_detail = {}
        venue_id, venue_name, artist_id, artist_name, artist_image_link, show_time = show_info[
            i]
        show_detail['venue_id'] = venue_id
        show_detail['venue_name'] = venue_name
        show_detail['artist_id'] = artist_id
        show_detail['artist_name'] = artist_name
        show_detail['artist_image_link'] = artist_image_link
        show_detail['start_time'] = str(show_time)
        data.append(show_detail)
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

    form = ShowForm(request.form)
    show_artist_id = form.artist_id.data
    try:
        show_venue_id = form.venue_id.data
        show_start_time = form.start_time.data

        show_details = Show(artist_id=show_artist_id,
                            venue_id=show_venue_id, start_time=show_start_time)
        db.session.add(show_details)
        db.session.commit()
  # on successful db insert, flash success
        flash('Show was successfully listed!')

    except BaseException:
        db.session.rollback()
        flash('An error occurred. Show ' + ' could not be listed.')
        logging.error("Error occired " + str())
        abort(404)
 # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#
import os 
# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
