module.exports = function(grunt) {
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json')
    , concat: {
        options: {
            // define a string to put between each file in the concatenated output
            separator: ';'
        },
        dist: {
            // the files to concatenate
            src: [
                 './bower_components/bootstrap/transition.js'
                ,'./bower_components/bootstrap/alert.js'
                ,'./bower_components/bootstrap/button.js'
                ,'./bower_components/bootstrap/carousel.js'
                ,'./bower_components/bootstrap/collapse.js'
                ,'./bower_components/bootstrap/dropdown.js'
                ,'./bower_components/bootstrap/modal.js'
                ,'./bower_components/bootstrap/tooltip.js'
                ,'./bower_components/bootstrap/popover.js'
                ,'./bower_components/bootstrap/scrollspy.js'
                ,'./bower_components/bootstrap/tab.js'
                ,'./bower_components/bootstrap/affix.js'
                ,'./bower_components/json3/lib/json3.js'
                ,'./bower_components/store/store.js'
                ,'./bower_components/underscore/underscore.js'
                ,'./bower_components/backbone/backbone.js'
                ,'./bower_components/jquery-validation/jquery.validate.js'
            ],
            // the location of the resulting JS file
            dest: '../webapp/ufostart/static/vendor/dist/libs.js'
        }
    }
    , uglify: {
        options: {
          // the banner is inserted at the top of the output
          banner: '/*! <%= pkg.name %> <%= grunt.template.today("dd-mm-yyyy") %> */\n'
        },
        dist: {
          files: {
            '../webapp/ufostart/static/vendor/dist/libs.min.js': ['<%= concat.dist.dest %>']
          }
        }
    }
    , copy: {
      main: {
        files: [
          {expand:true, src: ['./bower_components/hncajax/tools/*.js'], dest: '../webapp/ufostart/static/vendor/', rename: function(dest, src) {
              return dest + src.replace('./bower_components/hncajax/', '');
            }},
          {src: ['./bower_components/less.js/dist/less-1.4.0-beta.js'], dest: '../webapp/ufostart/static/vendor/dev/less.js'},
          {src: ['./bower_components/requirejs/require.js'], dest: '../webapp/ufostart/static/vendor/dev/require.js'}
        ]
      }
    }
  });
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-bower-task');
  
  grunt.registerTask('default', ['concat', 'uglify', "copy"]);
  grunt.registerTask('production', ['concat', 'uglify']);
}
