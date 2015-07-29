(function ($, Backbone, _, app){
    var AppRouter = Backbone.Router.extend({
        routes:{
            '':'home'
        },
        initialize: function(options){
            this.contentElement = "#content";
            this.current = null;
            Backbone.history.start();
        },
        home: function(){
            var view = new app.views.HomepageView({ el : this.contentElement });
            this.render(view);
        },
        route: function (route, name, callback){
            var login;
            callback = callback || this[name];
            callback = _.wrap(callback, function(original){
                var args = _.without(arguments, original);
                if(app.session.authenticated()){
                    original.apply(this, args);
                }else{
                    //Mostra a tela de login antes de chamar a view
                    $(this.contentElement).hide();
                    login = new app.views.LoginView();
                    $(this.contentElement).after(login.el);
                    login.on('done', function(){
                        $(this.contentElement).show();
                        original.apply(this, args)
                    }, this);
                    login.render();
                }
            });
            return Backbone.Router.prototype.route.apply(this, [route, name, callback]);
        },
        render: function(view){
            if(this.current){
                this.undelegateEvents();
                this.current.$el = $();
                this.current.remove();
            }
            this.current = view;
            this.current.render();
        }
    });

    app.router = AppRouter;

})(jQuery, Backbone, _, app);
