module.exports = function(grunt) {

    grunt.initConfig({
        bower: grunt.file.readJSON('bower.json'),
        clean: {
            dist: ['dist/*'],
            html: ['html/*.html'],
            tmp : ['.tmp','dist/css','dist/scripts','**/.DS_store']
        },
        copy: {
            dist: {
                files: [
                    {expand: true, cwd: 'html/', src: ['**', '!**/*.scss'], dest: 'dist/html/'},
                    {expand: true, cwd: 'assets/images', src: ['**'], dest: 'dist/html/images/'}
                ]
            },
            js: {
                files: [
                    {src: 'dist/scripts/app.min.js', dest : 'dist/html/scripts/app.min.js'},
                    {src: 'dist/css/styles/app.min.css', dest : 'dist/html/css/styles/app.min.css'}
                ]
            },
            libs:{
                files: '<%= bower.copy %>'
            }
        },
        htmlmin: {
            dist: {
                options: { removeComments: true, collapseWhitespace: true },
                files: [
                    { expand: true, cwd: 'dist/html/', src: ['*.html', '**/*.html'], dest: 'dist/html/' }
                ]
            }
        },
        watch: {
            sass: {
              files: ['html/css/scss/*.scss'],
              tasks: ['sass'],
            }
        },
        sass: {
            dist: {
                files: [
                    {'/static/css/styles/app.css': ['/static/css/scss/app.scss']},
                    {'/static/css/styles/app.rtl.css': ['/static/css/scss/app.rtl.scss']},
                    {'/static/css/bootstrap-rtl/dist/bootstrap-rtl.css': ['/static/css/bootstrap-rtl/scss/bootstrap-rtl.scss']},
                    {'/static/css/theme/primary.css': ['/static/css/scss/theme/primary.scss']},
                    {'/static/css/theme/accent.css': ['/static/css/scss/theme/accent.scss']},
                    {'/static/css/theme/warn.css': ['/static/css/scss/theme/warn.scss']},
                    {'/static/css/theme/success.css': ['/static/css/scss/theme/success.scss']},
                    {'/static/css/theme/info.css': ['/static/css/scss/theme/info.scss']},
                    {'/static/css/theme/blue.css': ['/static/css/scss/theme/blue.scss']},
                    {'/static/css/theme/warning.css': ['/static/css/scss/theme/warning.scss']},
                    {'/static/css/theme/danger.css': ['/static/css/scss/theme/danger.scss']}
                ]
            }
        },
        useminPrepare: {
            html: ['templates/*.html']
        },
        usemin: {
            html: ['dist/html/*.html']
        },
        bump: {
            options: {
                files: ['package.json'],
                commit: true,
                commitMessage: 'Release v%VERSION%',
                commitFiles: ['-a'],
                createTag: true,
                tagName: 'v%VERSION%',
                tagMessage: 'Version %VERSION%',
                push: true,
                pushTo: 'origin',
                gitDescribeOptions: '--tags --always --abbrev=1 --dirty=-d'
            }
        },
        assemble: {
          options: {
            layoutdir: 'views/layout/',
            partials: ['views/blocks/**/*.html' ],
            data: ['assets/data.json'],
            flatten: true,
            helpers: ['assets/assemble.js']
          },
          page: {
            options: {
              layout: 'layout.html'
            },
            src: [
                'views/**/*.html',
                '!views/blocks/**',
                '!views/layout/**'
            ],
            dest: 'html/'
          }
        }
    });

    grunt.loadNpmTasks('grunt-usemin');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-htmlmin');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-bump');
    grunt.loadNpmTasks('grunt-assemble');

    grunt.registerTask('build', [
        'clean:dist',
        'sass',
        'copy',
        'useminPrepare',
        'concat:generated',
        'cssmin:generated',
        'uglify:generated',
        'usemin',
        'htmlmin',
        'copy:js',
        'clean:tmp'
    ]);

    grunt.registerTask('release', [
        'bump'
    ]);

    grunt.registerTask('html', [
        'clean:html',
        'assemble'
    ]);
};
