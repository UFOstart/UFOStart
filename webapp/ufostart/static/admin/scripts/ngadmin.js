
var module = angular.module('adminapp', [])
  .filter('filter_active', function() {
    return function(input) {
        return input?'ACTIVE':'disabled'
    }
});

(function(module){
    function addFactory(module, key, getURL, getValues){
        module.factory(key, function($http, $q) {
            return {
              getAllItems: function(){
                var deferred = $q.defer();
                $http.post(getURL, {}
                ).success(function(data){
                  deferred.resolve(getValues(data));
                }).error(function(){
                  deferred.reject("An error occured while fetching items");
                });
              return deferred.promise;
            }}
        });
    }

    addFactory(module, "Templates", "/api/0.0.1/admin/template/all", function(data){return data.Templates});
    addFactory(module, "Needs", "/api/0.0.1/admin/need/all", function(data){return data.Needs});
    addFactory(module, "Services", "/api/0.0.1/admin/service/all", function(data){return data.Services});
    addFactory(module, "Static", "/api/0.0.1/admin/static", function(data){return data.Content.Static});

})(module);

function TemplateListCtrl($scope, Templates) {
  $scope.templates = [];
  $scope.queryStatus = 'true';
  Templates.getAllItems().then(function(data){
      $scope.templates = data
  });
  $scope.query = function (item){
        return    ((!$scope.queryName || !!~item.name.toLowerCase().indexOf($scope.queryName.toLowerCase()))
                && (!$scope.queryStatus || $scope.queryStatus == 'true' && item.active || $scope.queryStatus == 'false' && !item.active ))  ;
  };
}

function TaskListCtrl($scope, Needs) {
  $scope.tasks = [];

  Needs.getAllItems().then(function(data){
      $scope.tasks = data
  });
  $scope.query = function (item){
        return    (!$scope.queryName || !!~item.name.toLowerCase().indexOf($scope.queryName.toLowerCase()));
  };
}

function ServiceListCtrl($scope, Services) {
  $scope.services = [];

  Services.getAllItems().then(function(data){
      $scope.services = data
  });
  $scope.query = function (item){
        return    (!$scope.queryName || !!~item.name.toLowerCase().indexOf($scope.queryName.toLowerCase()));
  };
}

function StaticContentListCtrl($scope, Static) {
  $scope.contents = [];
  $scope.pages = [];
  Static.getAllItems().then(function(data){
      $scope.contents = data
      $scope.pages = _.sortBy(_.uniq(_.map(_.pluck(data, "key"), function(item){return item.split(".")[0]})), function(e){return e});
  });
  $scope.query = function (item){
        var key = item.key.toLowerCase();
        return    (!$scope.queryName || !!~key.indexOf($scope.queryName.toLowerCase()))
               && (!$scope.queryPage || key.indexOf($scope.queryPage.toLowerCase())==0);
  };
}
