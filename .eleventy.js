const pluginSEO = require("eleventy-plugin-seo");

module.exports = function(eleventyConfig) {
    eleventyConfig.addPassthroughCopy({ static: "/" });

    eleventyConfig.addPlugin(pluginSEO, {
        title: "Kyle B",
        description: "Kyle Brown's personal website and published articles",
        url: "https://kyleb.cc",
        author: "Kyle Brown",
        twitter: "kyleb_cc",
        options: {
            titleDivider: "|",
            showPageNumbers: false
        }
    })

    return {
        // Control which files Eleventy will process
        // e.g.: *.md, *.njk, *.html, *.liquid
        templateFormats: [
            "md",
            "njk",
            "html",
            "liquid"
        ],

        // Pre-process *.md files with: (default: `liquid`)
        markdownTemplateEngine: "njk",

        // Pre-process *.html files with: (default: `liquid`)
        htmlTemplateEngine: "njk",

        dir: {
            input: "src"
        }
    }
};
