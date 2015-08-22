(function ($, Backbone, _, app){

    //Funções auxiliares de CSRF
    function csrfSafeMethod(method){
        return (/^(GET|HEAD|OPTIONS|TRACE)$/i.test(method))
    }

    function getCookie(name){
        var cookieValue = null;
        if(document.cookie && document.cookie != ''){
            var cookies = document.cookie.split(';');
            for( var i = 0; i < cookies.length; i++ ){
                var cookie = $.trim(cookies[i]);
                if(cookie.substring(0, name.length+1) == (name + '=') ) {
                    cookieValue = decodeURIComponent( cookie.substring(name.length + 1) );
                    break;
                }
            }
        }
        return cookieValue;
    }

    $.ajaxPrefilter( function (settings, originalOptions, xhr){
        var csrfToken;
        if(!csrfSafeMethod(settings.type) && !this.crossDomain){
            csrfToken = getCookie('csrfToken');
            xhr.setRequestHeader('X-CSRFToken',csrfToken);
        }
    });

    var Session = Backbone.Model.extend({
        defaults:{
            token: null
        },
        initialize: function(options){
            this.options = options;
            $.ajaxPrefilter($.proxy(this._setupAuth, this));
            this.load();
        },
        load: function(){
            var token = localStorage.apiToken;
            if(token){
                this.set('token', token);
            }
        },
        save: function(token){
            this.set('token', token);
            if(token === null){
                localStorage.removeItem('apiToken');
            }else{
                localStorage.apiToken = token;
            }
        },
        delete: function(){
            this.save(null);
        },
        authenticated: function(){
            return this.get('token') !== null;
        },
        _setupAuth: function(settings, originalOptions, xhr){
            if( this.authenticated() ){
                xhr.setRequestHeader(
                    'Authorization',
                    'Token '+ this.get('token')
                );
            }
        }
    });

    app.session = new Session();

    var BaseModel = Backbone.Model.extend({
      url: function() {
        var links = this.get('links'),
          url = links && links.self;
        if (!url) {
            url = Backbone.Model.prototype.url.call(this);
        }
        return url;
      }
    });

    app.models.Sprint = BaseModel.extend({
      fetchTasks: function(){
        var links = this.get('links');
        if(links && links.tasks){
          app.tasks.fetch({url: links.tasks, remove: false});
        }
      }
    });
    app.models.Task = BaseModel.extend({});
    app.models.User = BaseModel.extend({
      idAttributemodel: 'username'
    });

    var BaseCollection = Backbone.Collection.extend({
      parse: function (response){
        this._next = response.next;
        this._previous = response.previous;
        this._count = response.count;
        return response.results || [];
      },
      getOrFetch: function (id) {
        var result = $.Deferred(),
          model = this.get(id);
        if(!model) {
          model = this.push({id: id});
          model.fetch({
            success: function (model, response, options) {
              result.resolve(model);
            },
            error: function (model, response, options) {
              result.reject(model, response);
            }
          });
        } else {
          result.resolve(model);
        }
        return result;
      }
    });

    app.collections.ready = $.getJSON(app.apiRoot);
    app.collections.ready.done(function (data){

      app.collections.Sprints = BaseCollection.extend({
        model: app.models.Sprint,
        url: data.sprints
      });
      app.sprints = new app.collections.Sprints();

      app.collections.Tasks = BaseCollection.extend({
        model: app.models.Task,
        url: data.tasks,
        getBacklog: function(){
          this.fetch({remove: false, data: {backlog: 'True'} });
        }
      });
      app.tasks = new app.collections.Tasks();

      app.collections.Users = BaseCollection.extend({
        model: app.models.User,
        url: data.users
      });
      app.users = new app.collections.Users();

    });


})(jQuery, Backbone, _, app);
