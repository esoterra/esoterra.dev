const pluginSEO = require("eleventy-plugin-seo");
const syntaxHighlight = require("@11ty/eleventy-plugin-syntaxhighlight");
const { DateTime } = require("luxon");

module.exports = function(eleventyConfig) {
    eleventyConfig.addPassthroughCopy({ static: "/" });

    eleventyConfig.addPlugin(syntaxHighlight);

    eleventyConfig.addPlugin(pluginSEO, {
        title: "Esoterra",
        description: "My personal website",
        url: "https://esoterra.dev",
        options: {
            titleDivider: "|",
            showPageNumbers: false
        }
    });

    // {{ date | friendlyDate('OPTIONAL FORMAT STRING') }}
    // List of supported tokens: https://moment.github.io/luxon/docs/manual/formatting.html#table-of-tokens
    eleventyConfig.addFilter("date", function(dateObj, format = 'LLLL d, y') {
        return DateTime.fromJSDate(dateObj).toFormat(format);
    });

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
