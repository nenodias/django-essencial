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
                    'Token'+ this.get('token')
                );
            }
        }
    });

    app.session = new Session();
})(jQuery, Backbone, _, app);
