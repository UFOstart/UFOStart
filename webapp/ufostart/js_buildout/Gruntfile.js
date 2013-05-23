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
                './bootstrap/*.js',
                './bower_components/json3/lib/json3.js',
                './bower_components/underscore/underscore.js',
                './bower_components/backbone/backbone.js',
                './bower_components/parsleyjs/parsley.min.js',
                './bower_components/requirejs/require.js',
            ],
            // the location of the resulting JS file
            dest: '../static/scripts/dist/libs.js'
        }
    }
    , uglify: {
        options: {
          // the banner is inserted at the top of the output
          banner: '/*! <%= pkg.name %> <%= grunt.template.today("dd-mm-yyyy") %> */\n'
        },
        dist: {
          files: {
            '../static/scripts/dist/libs.min.js': ['<%= concat.dist.dest %>']
          }
        }
    }
    , copy: {
      main: {
        files: [
          {src: ['./bower_components/less.js/dist/less-1.4.0-beta.js'], dest: '../static/scripts/dist/less.js'},
        ]
      }
    }
  });
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-copy');

  grunt.registerTask('development', ['concat', 'uglify', "copy"]);
  grunt.registerTask('production', ['concat', 'uglify']);
}
