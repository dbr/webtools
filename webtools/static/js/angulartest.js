var app = angular.module('test', ['ngResource', 'ngRoute']).
  config(function($interpolateProvider) {
      $interpolateProvider.startSymbol("{!");
      $interpolateProvider.endSymbol("!}");
  });

app.config(['$routeProvider',
            function($routeProvider){
                $routeProvider.
                    when('/channels', {
                        templateUrl: '/static/partials/channel-list.html',
                        controller: 'ChannelList'
                    }).
                    when('/channels/:id', {
                        'templateUrl': '/static/partials/channel-view.html',
                        controller: 'ChannelView'
                    }).
                    otherwise({
                        redirectTo: '/channels'
                    });
            }]);


app.controller(
    "ChannelList",
    function ChannelList($scope, $resource, $http){

        $scope.filtertext = "";
        $scope.status = "";

        $scope.init = function(){
            console.log("Channel list init");
            $scope.refresh();
        }

        $scope.refresh = function(){
            console.log("Refreshing");
            $scope.status = "Loading";

            $http({method: 'GET', url: '/youtube/api/1/channels'}).
                success(function(data, status, headers, config){
                    console.log("Yay");
                    console.log(data);

                    $scope.data = data;

                    $scope.loading="";
                }).
                error(function(data, status, headers, config){
                    console.log("boo");
                    $scope.loading="";
                });
        }
    });


app.controller(
    "ChannelView",
    function ChannelView($scope, $routeParams, $http){
        $scope.id = $routeParams.id;
        console.log("Viewing channel" + $scope.id);

        $http.get('/youtube/api/1/channels/' + $scope.id).success(function(data) {
            $scope.data = data;
        });
    });

