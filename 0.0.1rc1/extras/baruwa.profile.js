dependencies = {
    action: "release",
    optimize: "shrinksafe",
    layerOptimize: "shrinksafe",
    copyTests: false,
    loader: "default",
    cssOptimize: "comments",
    version: "1.4.1",
	stripConsole: "all",
    localeList: "en-us",
    layers: [
		{
			name:"dojo.js",
			customBase: false,
			dependencies:[
			]
		},
        {
            name:"pie.js",
            dependencies:[
                "dojox.charting.Chart2D",
                "dojox.charting.plot2d.Pie",
                "dojox.charting.action2d.Highlight",
                "dojox.charting.action2d.MoveSlice",
                "dojox.charting.action2d.Tooltip",
                "dojox.charting.themes.MiamiNice",
                "dojox.gfx.svg"
            ]
        },
        {
            name:"bar.js",
            dependencies:[
                "dojox.charting.Chart2D",
                "dojox.gfx.svg"
            ]
        },
        {
            name:"listing.js",
            dependencies:[
                "dojox.charting.Chart2D",
                "dojox.charting.action2d.Highlight",
                "dojox.charting.action2d.Magnify",
                "dojox.charting.action2d.Shake",
                "dojox.charting.action2d.Tooltip",
                "dojox.charting.widget.Legend",
                "dojox.gfx.svg"
            ]
        }
    ],
    prefixes: [
        ["dijit", "../dijit"],
        ["dojox", "../dojox"]
    ]
}
