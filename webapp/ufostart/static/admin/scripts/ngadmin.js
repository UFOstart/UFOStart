
var module = angular.module('adminapp', [])
  .filter('filter_active', function() {
    return function(input) {
        return input?'ACTIVE':'disabled'
    }
});

(function(module){
    function addFactory(module, key, url){
        module.factory(key, function($http, $q) {
            return {
              getAllItems: function(){
                var deferred = $q.defer();
                $http.post(url, {}
                ).success(function(data){
                  deferred.resolve(data[key]);
                }).error(function(){
                  deferred.reject("An error occured while fetching items");
                });
              return deferred.promise;
            }
          }
      });
    }

    addFactory(module, "Templates", "/api/0.0.1/admin/template/all");
    addFactory(module, "Needs", "/api/0.0.1/admin/need/all");
    addFactory(module, "Services", "/api/0.0.1/admin/service/all");

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

function NeedListCtrl($scope, Needs) {
  $scope.needs = [];

  Needs.getAllItems().then(function(data){
      $scope.needs = data
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
