var app = angular.module('test', ['ngResource', 'ngRoute', 'ngTable'])
    .config(function($interpolateProvider) {
      $interpolateProvider.startSymbol("{!").endSymbol("!}");
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
        $scope.loading = false;

        $scope.init = function(){
            console.log("Channel list init");
            $scope.refresh();
        }

        $scope.refresh = function(){
            console.log("Refreshing");
            $scope.loading = true;

            $http({method: 'GET', url: '/youtube/api/1/channels'}).
                success(function(data, status, headers, config){
                    console.log("Yay");
                    console.log(data);

                    $scope.data = data;

                    $scope.loading=false;
                }).
                error(function(data, status, headers, config){
                    console.log("boo");
                    $scope.loading="";
                });
        }
    });


app.controller(
    "ChannelView",
    function ($scope, $routeParams, $http){
        // Initialisation
        $scope.id = $routeParams.id;
        console.log("Viewing channel" + $scope.id);

        $http.get('/youtube/api/1/channels/' + $scope.id).success(function(data) {
            $scope.data = data;
            console.log(data);
        });

        // Actions
        $scope.download = function(video){
            console.log("Download", video.id);
        }

        $scope.mark_viewed = function(video){
            console.log("Mark as viewed", video.id);
        }
        $scope.mark_ignored = function(video){
            console.log("Mark as ignored", video.id);
        }

        // Helper
        $scope.status = function(video){
            return {
                NE: "new",
                GR: "grabbed",
            }[video.status] || video.status;
        }
    });



app.controller('DemoCtrl', function($scope, $timeout, $resource, ngTableParams, $location) {
    var Api = $resource('/youtube/api/1/channels');

    $scope.tableParams = new ngTableParams(
        angular.extend(
            {
                page: 1,
                count: 2,
                sorting: {
                    name: 'asc'     // initial sorting
                }
            },
            $location.search()),
        {
            total: 0,           // length of data
            getData: function($defer, params) {
                $location.search(params.url());
                // ajax request to api
                Api.get(params.url(), function(data) {
                    $timeout(function() {
                        // update table params
                        params.total(data.total);
                        // set new data
                        $defer.resolve(data.channels);
                    }, 500);
                });
            }
        });
});
