/*
 * Created on Oct 25, 2006
 *
 */
package com.fusioncharts;

import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

/**
 * Contains methods to add no cache string to a url,getting colors for the
 * charts.<br>
 * This class can be used to create chart xml given the swf filename and other<br>
 * parameters.<br>
 * In order to use this class in your jsps,import this class and<br>
 * call the appropriate method directly as follows:<br>
 * FusionChartsHelper.addCacheToDataURL(...);<br>
 * In order to use this class for colors call the method as shown:<br>
 * FusionChartsHelper helper = new FusionChartsHelper();<BR>
 * String bgColor = helper.getFCColor();<BR>
 * 
 * @author InfoSoft Global (P) Ltd.
 */
public class FusionChartsHelper {

	/*
	 * This page contains an array of colors to be used as default set of colors
	 * for FusionCharts 'arr_FCColors is the array that would contain the hex
	 * code of colors 'ALL COLORS HEX CODES TO BE USED WITHOUT #
	 */

	/**
	 * Adds additional string to the url to and encodes the parameters,<br>
	 * so as to disable caching of data.<br>
	 * 
	 * @param strDataURL
	 *            - dataURL to be fed to chart
	 * @return cachedURL - URL with the additional string added
	 */

	public static String addCacheToDataURL(String strDataURL) {
		String cachedURL = strDataURL;
		// Add the no-cache string if required

		// We add ?FCCurrTime=xxyyzz
		// If the dataURL already contains a ?, we add &FCCurrTime=xxyyzz
		// We replace : with _, as FusionCharts cannot handle : in URLs
		Calendar nowCal = Calendar.getInstance();
		Date now = nowCal.getTime();
		SimpleDateFormat sdf = new SimpleDateFormat("MM/dd/yyyy HH_mm_ss a");
		String strNow = sdf.format(now);

		try {

			if (strDataURL.indexOf("?") > 0) {
				cachedURL = strDataURL + "&FCCurrTime="
						+ URLEncoder.encode(strNow, "UTF-8");
			} else {
				cachedURL = strDataURL + "?FCCurrTime="
						+ URLEncoder.encode(strNow, "UTF-8");
			}

		} catch (UnsupportedEncodingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			cachedURL = strDataURL + "?FCCurrTime=" + strNow;
		}

		return cachedURL;
	}

	/**
	 * Converts a Boolean value to int value<br>
	 * 
	 * @param bool
	 *            Boolean value which needs to be converted to int value
	 * @return int value correspoding to the boolean : 1 for true and 0 for
	 *         false
	 */
	public static int boolToNum(Boolean bool) {
		int num = 0;
		if (bool.booleanValue()) {
			num = 1;
		}
		return num;
	}

	/**
	 * Creates the JavaScript + HTML code required to embed a chart.<br>
	 * Uses the javascript FusionCharts class to create the chart by supplying <br>
	 * the required parameters to it.<br>
	 * Note: Only one of the parameters strURL or strXML has to be not null for
	 * this<br>
	 * method to work. If both the parameters are provided then strURL is used
	 * for further processing.<br>
	 * 
	 * @param chartSWF
	 *            - SWF File Name (and Path) of the chart which you intend to
	 *            plot
	 * @param strURL
	 *            - If you intend to use dataURL method for this chart, pass the
	 *            URL as this parameter. Else, set it to "" (in case of dataXML
	 *            method)
	 * @param strXML
	 *            - If you intend to use dataXML method for this chart, pass the
	 *            XML data as this parameter. Else, set it to "" (in case of
	 *            dataURL method)
	 * @param chartId
	 *            - Id for the chart, using which it will be recognized in the
	 *            HTML page. Each chart on the page needs to have a unique Id.
	 * @param chartWidth
	 *            - Intended width for the chart (in pixels)
	 * @param chartHeight
	 *            - Intended height for the chart (in pixels)
	 * @param debugMode
	 *            - Whether to start the chart in debug mode
	 * @param registerWithJS
	 *            - Whether to ask chart to register itself with JavaScript
	 * @deprecated
	 */
	@Deprecated
	public static String createChart(String chartSWF, String strURL,
			String strXML, String chartId, int chartWidth, int chartHeight,
			boolean debugMode, boolean registerWithJS) {
		StringBuffer strBuf = new StringBuffer();
		// First we create a new DIV for each chart. We specify the name of DIV
		// as "chartId"Div.
		// DIV names are case-sensitive.

		strBuf.append("\t\t<!-- START Script Block for Chart-->\n");
		strBuf.append("\t\t<div id='" + chartId + "Div' align='center'>\n");
		strBuf.append("\t\t\t\tChart.\n");

		/*
		 * The above text "Chart" is shown to users before the chart has started
		 * loading (if there is a lag in relaying SWF from server). This text is
		 * also shown to users who do not have Flash Player installed. You can
		 * configure it as per your needs.
		 */

		strBuf.append("\t\t</div>\n");

		/*
		 * Now, we create the chart using FusionCharts js class. Each chart's
		 * instance (JavaScript) Id is named as chart_"chartId".
		 */

		strBuf.append("\t\t<script type='text/javascript'>\n");
		// Instantiate the Chart
		Boolean registerWithJSBool = new Boolean(registerWithJS);
		Boolean debugModeBool = new Boolean(debugMode);
		int regWithJSInt = boolToNum(registerWithJSBool);
		int debugModeInt = boolToNum(debugModeBool);

		strBuf.append("\t\t\t\tvar chart_" + chartId + " = new FusionCharts('"
				+ chartSWF + "', '" + chartId + "', '" + chartWidth + "', '"
				+ chartHeight + "', '" + debugModeInt + "', '" + regWithJSInt
				+ "');\n");
		// Check whether we've to provide data using dataXML method or dataURL
		// method
		if (strXML.equals("")) {
			strBuf.append("\t\t\t\t// Set the dataURL of the chart\n");
			strBuf.append("\t\t\t\tchart_" + chartId + ".setXMLUrl(\"" + strURL
					+ "\", \"xml\");\n");
		} else {
			strBuf
					.append("\t\t\t\t// Provide entire XML data using dataXML method\n");
			strBuf.append("\t\t\t\tchart_" + chartId + ".setXMLData(\""
					+ strXML + "\");\n");
		}
		strBuf.append("\t\t\t\t// Finally, render the chart.\n");
		strBuf.append("\t\t\t\tchart_" + chartId + ".render(\"" + chartId
				+ "Div\");\n");
		strBuf.append("\t\t</script>\n");
		strBuf.append("\t\t<!--END Script Block for Chart-->\n");
		return strBuf.substring(0);
	}

	// getFCColor method helps return a bgColor from arr_FCColors array. It uses
	// cyclic iteration to return a bgColor from a given index. The index value
	// is
	// maintained in FC_ColorCounter

	/**
	 * New method to handle all data formats supported by FusionCharts JS API
	 * version >= 3.2
	 * 
	 * @param chartSWF
	 * @param strURL
	 * @param strData
	 * @param dataFormat
	 * @param chartId
	 * @param chartWidth
	 * @param chartHeight
	 * @param debugMode
	 * @param registerWithJS
	 * @return
	 */
	public static String createChart(String chartSWF, String strURL,
			String strData, String dataFormat, String chartId,
			String chartWidth, String chartHeight, boolean debugMode,
			boolean registerWithJS) {
		StringBuffer strBuf = new StringBuffer();
		// First we create a new DIV for each chart. We specify the name of DIV
		// as "chartId"Div.
		// DIV names are case-sensitive.

		strBuf.append("\t\t<!-- START Script Block for Chart-->\n");
		strBuf.append("\t\t<div id='" + chartId + "Div' align='center'>\n");
		strBuf.append("\t\t\t\tChart.\n");

		/*
		 * The above text "Chart" is shown to users before the chart has started
		 * loading (if there is a lag in relaying SWF from server). This text is
		 * also shown to users who do not have Flash Player installed. You can
		 * configure it as per your needs.
		 */

		strBuf.append("\t\t</div>\n");

		/*
		 * Now, we create the chart using FusionCharts js class. Each chart's
		 * instance (JavaScript) Id is named as chart_"chartId".
		 */

		strBuf.append("\t\t<script type='text/javascript'>\n");
		// Instantiate the Chart
		Boolean registerWithJSBool = new Boolean(registerWithJS);
		Boolean debugModeBool = new Boolean(debugMode);
		int regWithJSInt = boolToNum(registerWithJSBool);
		int debugModeInt = boolToNum(debugModeBool);

		strBuf.append("\t\t\t\tvar chart_" + chartId + " = new FusionCharts('"
				+ chartSWF + "', '" + chartId + "', '" + chartWidth + "', '"
				+ chartHeight + "', " + debugModeInt + ", " + regWithJSInt
				+ ");\n");
		// Check whether we've to provide data using dataXML method or dataURL
		// method

		if (strData == null || strData.equals("")) {
			strBuf.append("\t\t\t\t// Set the dataURL of the chart\n");
			strBuf.append("\t\t\t\tchart_" + chartId + ".setChartDataUrl(\""
					+ strURL + "\",\"" + dataFormat + "\");\n");
			/*
			 * strBuf.append("\t\t\t\tchart_" + chartId + ".setDataURL(\"" +
			 * strURL + "\");\n");
			 */
		} else {
			strBuf
					.append("\t\t\t\t// Provide entire XML data using dataXML method\n");
			strBuf.append("\t\t\t\tchart_" + chartId + ".setChartData(\""
					+ strData + "\",\"" + dataFormat + "\");\n");
		}
		strBuf.append("\t\t\t\t// Finally, render the chart.\n");
		strBuf.append("\t\t\t\tchart_" + chartId + ".render(\"" + chartId
				+ "Div\");\n");
		strBuf.append("\t\t</script>\n");
		strBuf.append("\t\t<!--END Script Block for Chart-->\n");
		return strBuf.substring(0);
	}

	/**
	 * New method to handle 1. all data formats supported by FusionCharts JS API
	 * version >= 3.2 2. all parameters accepted by FusionCharts
	 * 
	 * @param chartSWF
	 * @param strURL
	 * @param strData
	 * @param dataFormat
	 * @param chartId
	 * @param chartWidth
	 * @param chartHeight
	 * @param debugMode
	 * @param registerWithJS
	 * @param bgColor
	 * @param scaleMode
	 * @param lang
	 * @param detectFlashVersion
	 * @param autoInstallRedirect
	 * @param wMode
	 * @return
	 */
	public static String createChart(String chartSWF, String strURL,
			String strData, String dataFormat, String chartId,
			String chartWidth, String chartHeight, boolean debugMode,
			boolean registerWithJS, String bgColor, String scaleMode,
			String lang, String detectFlashVersion, String autoInstallRedirect,
			String windowMode) {
		StringBuffer strBuf = new StringBuffer();
		// First we create a new DIV for each chart. We specify the name of DIV
		// as "chartId"Div.
		// DIV names are case-sensitive.

		strBuf.append("\t\t<!-- START Script Block for Chart-->\n");
		strBuf.append("\t\t<div id='" + chartId + "Div' align='center'>\n");
		strBuf.append("\t\t\t\tChart.\n");

		/*
		 * The above text "Chart" is shown to users before the chart has started
		 * loading (if there is a lag in relaying SWF from server). This text is
		 * also shown to users who do not have Flash Player installed. You can
		 * configure it as per your needs.
		 */

		strBuf.append("\t\t</div>\n");

		/*
		 * Now, we create the chart using FusionCharts js class. Each chart's
		 * instance (JavaScript) Id is named as chart_"chartId".
		 */

		strBuf.append("\t\t<script type='text/javascript'>\n");
		// Instantiate the Chart
		Boolean registerWithJSBool = new Boolean(registerWithJS);
		Boolean debugModeBool = new Boolean(debugMode);
		int regWithJSInt = boolToNum(registerWithJSBool);
		int debugModeInt = boolToNum(debugModeBool);

		windowMode = (windowMode == null) ? "" : windowMode;
		bgColor = (bgColor == null) ? "" : bgColor;
		scaleMode = (scaleMode == null) ? "" : scaleMode;
		lang = (lang == null) ? "" : lang;
		detectFlashVersion = (detectFlashVersion == null) ? ""
				: detectFlashVersion;
		autoInstallRedirect = (autoInstallRedirect == null) ? ""
				: autoInstallRedirect;

		strBuf.append("\t\t\t\tvar chart_" + chartId + " = new FusionCharts('"
				+ chartSWF + "', '" + chartId + "', '" + chartWidth + "', '"
				+ chartHeight + "', " + debugModeInt + ", " + regWithJSInt
				+ ", '" + bgColor + "', '" + scaleMode + "', '" + lang + "', '"
				+ detectFlashVersion + "', '" + autoInstallRedirect + "');\n");

		// Before rendering set the wMode
		if (windowMode != null && !windowMode.equals("")) {
			boolean transparency = false;
			if (windowMode.equalsIgnoreCase("transparent")
					|| windowMode.equalsIgnoreCase("opaque")) {
				transparency = windowMode.equalsIgnoreCase("transparent") ? true
						: false;
				strBuf.append("\t\t\tchart_" + chartId + ".setTransparent("
						+ transparency + ");\n");
			}

			// Any other value will be ignored.
		}

		// Check whether we've to provide data using dataXML method or dataURL
		// method

		if (strData == null || strData.equals("")) {
			strBuf.append("\t\t\t\t// Set the dataURL of the chart\n");
			strBuf.append("\t\t\t\tchart_" + chartId + ".setChartDataURL(\""
					+ strURL + "\",\"" + dataFormat + "\");\n");
		} else {
			strBuf
					.append("\t\t\t\t// Provide entire XML data using dataXML method\n");
			strBuf.append("\t\t\t\tchart_" + chartId + ".setChartData(\""
					+ strData + "\",\"" + dataFormat + "\");\n");
		}
		strBuf.append("\t\t\t\t// Finally, render the chart.\n");
		strBuf.append("\t\t\t\tchart_" + chartId + ".render(\"" + chartId
				+ "Div\");\n");
		strBuf.append("\t\t</script>\n");
		strBuf.append("\t\t<!--END Script Block for Chart-->\n");
		return strBuf.substring(0);
	}

	/**
	 * Creates the object tag required to embed a chart. Generates the object
	 * tag to embed the swf directly into the html page.<br>
	 * Note: Only one of the parameters strURL or strXML has to be not null for
	 * this<br>
	 * method to work. If both the parameters are provided then strURL is used
	 * for further processing.<br>
	 * 
	 * @param chartSWF
	 *            - SWF File Name (and Path) of the chart which you intend to
	 *            plot
	 * @param strURL
	 *            - If you intend to use dataURL method for this chart, pass the
	 *            URL as this parameter. Else, set it to "" (in case of dataXML
	 *            method)
	 * @param strXML
	 *            - If you intend to use dataXML method for this chart, pass the
	 *            XML data as this parameter. Else, set it to "" (in case of
	 *            dataURL method)
	 * @param chartId
	 *            - Id for the chart, using which it will be recognized in the
	 *            HTML page. Each chart on the page needs to have a unique Id.
	 * @param chartWidth
	 *            - Intended width for the chart (in pixels)
	 * @param chartHeight
	 *            - Intended height for the chart (in pixels)
	 * @param debugMode
	 *            - Whether to start the chart in debug mode
	 * 
	 */
	public static String createChartHTML(String chartSWF, String strURL,
			String strXML, String chartId, String chartWidth,
			String chartHeight, boolean debugMode) { /*
													 * Generate the FlashVars
													 * string based on whether
													 * dataURL has been provided
													 * or dataXML.
													 */
		String strFlashVars = "";
		Boolean debugModeBool = new Boolean(debugMode);

		if (strXML.equals("")) {
			// DataURL Mode
			strFlashVars = "chartWidth=" + chartWidth + "&chartHeight="
					+ chartHeight + "&debugMode=" + boolToNum(debugModeBool)
					+ "&dataURL=" + strURL + "";
		} else {
			// DataXML Mode
			strFlashVars = "chartWidth=" + chartWidth + "&chartHeight="
					+ chartHeight + "&debugMode=" + boolToNum(debugModeBool)
					+ "&dataXML=" + strXML + "";
		}
		StringBuffer strBuf = new StringBuffer();

		strBuf.append("\t\t<!--START Code Block for Chart-->\n");
		strBuf
				.append("\t\t<object classid='clsid:d27cdb6e-ae6d-11cf-96b8-444553540000' codebase='http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0' width='"
						+ chartWidth
						+ "' height='"
						+ chartHeight
						+ "' id='"
						+ chartId + "'>\n");
		strBuf
				.append("\t\t\t\t<param name='allowScriptAccess' value='always' />\n");
		strBuf.append("\t\t\t\t<param name='movie' value='" + chartSWF
				+ "'/>\n");
		strBuf.append("\t\t\t\t<param name='FlashVars' value=\"" + strFlashVars
				+ "\" />\n");
		strBuf.append("\t\t\t\t<param name='quality' value='high' />\n");
		strBuf
				.append("\t\t\t\t<embed src='"
						+ chartSWF
						+ "' FlashVars=\""
						+ strFlashVars
						+ "\" quality='high' width='"
						+ chartWidth
						+ "' height='"
						+ chartHeight
						+ "' name='"
						+ chartId
						+ "' allowScriptAccess='always' type='application/x-shockwave-flash' pluginspage='http://www.macromedia.com/go/getflashplayer' />\n");
		strBuf.append("\t\t</object>\n");
		strBuf.append("\t\t<!--END Code Block for Chart-->\n");
		return strBuf.substring(0);
	}

	/**
	 * Handles all the parameters including bgColor, scaleMode, lang and wmode
	 * Creates the object tag required to embed a chart. Generates the object
	 * tag to embed the swf directly into the html page.<br>
	 * Note: Only one of the parameters strURL or strXML has to be not null for
	 * this<br>
	 * method to work. If both the parameters are provided then strURL is used
	 * for further processing.<br>
	 * 
	 * @param chartSWF
	 * @param strURL
	 * @param strXML
	 * @param chartId
	 * @param chartWidth
	 * @param chartHeight
	 * @param debugMode
	 * @param bgColor
	 * @param scaleMode
	 * @param lang
	 * @param wMode
	 * @return
	 */
	public static String createChartHTML(String chartSWF, String strURL,
			String strXML, String chartId, String chartWidth,
			String chartHeight, boolean debugMode, String bgColor,
			String scaleMode, String lang, String windowMode) {
		/*
		 * Generate the FlashVars string based on whether dataURL has been
		 * provided or dataXML.
		 */
		String strFlashVars = "";
		Boolean debugModeBool = new Boolean(debugMode);

		windowMode = (windowMode == null) ? "" : windowMode;
		bgColor = (bgColor == null) ? "" : bgColor;
		scaleMode = (scaleMode == null) ? "" : scaleMode;
		lang = (lang == null) ? "" : lang;

		if (strXML.equals("")) {
			// DataURL Mode
			strFlashVars = "chartWidth=" + chartWidth + "&chartHeight="
					+ chartHeight + "&debugMode=" + boolToNum(debugModeBool)
					+ "&dataURL=" + strURL + "";
		} else {
			// DataXML Mode
			strFlashVars = "chartWidth=" + chartWidth + "&chartHeight="
					+ chartHeight + "&debugMode=" + boolToNum(debugModeBool)
					+ "&dataXML=" + strXML + "";
		}
		strFlashVars += "&scaleMode=" + scaleMode + "&lang=" + lang;

		StringBuffer strBuf = new StringBuffer();

		strBuf.append("\t\t<!--START Code Block for Chart-->\n");
		strBuf
				.append("\t\t<object classid='clsid:d27cdb6e-ae6d-11cf-96b8-444553540000' codebase='http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0' width='"
						+ chartWidth
						+ "' height='"
						+ chartHeight
						+ "' id='"
						+ chartId + "'>\n");
		strBuf
				.append("\t\t\t\t<param name='allowScriptAccess' value='always' />\n");
		strBuf.append("\t\t\t\t<param name='movie' value='" + chartSWF
				+ "'/>\n");
		strBuf.append("\t\t\t\t<param name='FlashVars' value=\"" + strFlashVars
				+ "\" />\n");
		strBuf.append("\t\t\t\t<param name='quality' value='high' />\n");
		strBuf.append("\t\t\t\t<param name='wmode' value='" + windowMode
				+ "'/>\n");
		strBuf.append("\t\t\t\t<param name='bgcolor' value='" + bgColor
				+ "'/>\n");
		strBuf
				.append("\t\t\t\t<embed src='"
						+ chartSWF
						+ "' FlashVars=\""
						+ strFlashVars
						+ "\" quality='high' width='"
						+ chartWidth
						+ "' height='"
						+ chartHeight
						+ "' name='"
						+ chartId
						+ "' wMode='"
						+ windowMode
						+ "'"
						+ " bgcolor='"
						+ bgColor
						+ "'>"
						+ "' allowScriptAccess='always' type='application/x-shockwave-flash' pluginspage='http://www.macromedia.com/go/getflashplayer' />\n");
		strBuf.append("\t\t</object>\n");
		strBuf.append("\t\t<!--END Code Block for Chart-->\n");
		return strBuf.substring(0);
	}

	public static String createChartWithJSON(String chartSWF, String strURL,
			String strData, String chartId, String chartWidth,
			String chartHeight, boolean debugMode, boolean registerWithJS) {
		return createChart(chartSWF, strURL, strData, "json", chartId,
				chartWidth, chartHeight, debugMode, registerWithJS);
	}

	public static String createChartWithJSON(String chartSWF, String strURL,
			String strData, String chartId, String chartWidth,
			String chartHeight, boolean debugMode, boolean registerWithJS,
			String bgColor, String scaleMode, String lang,
			String detectFlashVersion, String autoInstallRedirect,
			String windowMode) {
		return createChart(chartSWF, strURL, strData, "json", chartId,
				chartWidth, chartHeight, debugMode, registerWithJS, bgColor,
				scaleMode, lang, detectFlashVersion, autoInstallRedirect,
				windowMode);
	}

	public static String createChartWithXML(String chartSWF, String strURL,
			String strData, String chartId, String chartWidth,
			String chartHeight, boolean debugMode, boolean registerWithJS) {
		return createChart(chartSWF, strURL, strData, "xml", chartId,
				chartWidth, chartHeight, debugMode, registerWithJS);
	}

	public static String createChartWithXML(String chartSWF, String strURL,
			String strData, String chartId, String chartWidth,
			String chartHeight, boolean debugMode, boolean registerWithJS,
			String bgColor, String scaleMode, String lang,
			String detectFlashVersion, String autoInstallRedirect,
			String windowMode) {
		return createChart(chartSWF, strURL, strData, "xml", chartId,
				chartWidth, chartHeight, debugMode, registerWithJS, bgColor,
				scaleMode, lang, detectFlashVersion, autoInstallRedirect,
				windowMode);
	}

	/**
	 * Encodes the dataURL before it's served to FusionCharts. If you have
	 * parameters in your dataURL, you necessarily need to encode it.
	 * 
	 * @param strDataURL
	 *            - dataURL to be fed to chart
	 * @param addNoCacheStr
	 *            - Whether to add additional string to URL to disable caching
	 *            of data
	 * @return String - the encoded URL
	 */

	public static String encodeDataURL(String strDataURL, boolean addNoCacheStr) {
		String encodedURL = strDataURL;
		// Add the no-cache string if required
		if (addNoCacheStr) {
			/*
			 * We add ?FCCurrTime=xxyyzz If the dataURL already contains a ?, we
			 * add &FCCurrTime=xxyyzz We send the date separated with '_',
			 * instead of the usual ':' as FusionCharts cannot handle : in URLs
			 */
			java.util.Calendar nowCal = java.util.Calendar.getInstance();
			java.util.Date now = nowCal.getTime();
			java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat(
					"MM/dd/yyyy HH_mm_ss a");
			String strNow = sdf.format(now);
			if (strDataURL.indexOf("?") > 0) {
				strDataURL = strDataURL + "&FCCurrTime=" + strNow;
			} else {
				strDataURL = strDataURL + "?FCCurrTime=" + strNow;
			}
		}
		try {
			encodedURL = URLEncoder.encode(strDataURL, "UTF8");
		} catch (UnsupportedEncodingException e) {
			// TODO Auto-generated catch block
			encodedURL = strDataURL;
		}

		return encodedURL;
	}

	public static String obtainUTFBOMAsString() {
		byte[] utf8Bom = new byte[] { (byte) 0xef, (byte) 0xbb, (byte) 0xbf };
		String utf8BomStr;
		try {
			utf8BomStr = new String(utf8Bom, "UTF-8");
		} catch (UnsupportedEncodingException e) {
			utf8BomStr = new String(utf8Bom);
		}
		return utf8BomStr;
	}

	// We also initiate a counter variable to help us cyclically rotate through
	// the array of colors.
	int FC_ColorCounter = 0;
	protected String UTFBOMString = "";

	String[] arr_FCColors = new String[] { "1941A5", "AFD8F8", "F6BD0F",
			"8BBA00", "A66EDD", "F984A1", "CCCC00", "999999", "0099CC",
			"FF0000", "006F00", "0099FF", "FF66CC", "669966", "7C7CB4",
			"FF9933", "9900FF", "99FFCC", "CCCCFF", "669900", };

	/*
	 * "1941A5"; //Dark Blue "CCCC00"; //Chrome Yellow+Green "999999"; //Grey
	 * "0099CC"; //Blue Shade "FF0000"; //Bright Red "006F00"; //Dark Green
	 * "0099FF"; //Blue (Light) "FF66CC"; //Dark Pink "669966"; //Dirty green
	 * "7C7CB4"; //Violet shade of blue "FF9933"; //Orange "9900FF"; //Violet
	 * "99FFCC";//Blue+Green Light "CCCCFF"; //Light violet "669900"; //Shade of
	 * green
	 */

	public String getFCColor() {
		// Update index
		FC_ColorCounter += 1;
		// Return bgColor
		return arr_FCColors[FC_ColorCounter % arr_FCColors.length];

	}

}
