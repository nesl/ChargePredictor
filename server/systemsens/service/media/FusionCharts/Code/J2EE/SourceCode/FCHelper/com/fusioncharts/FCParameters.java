/**
 * 
 */
package com.fusioncharts;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Set;

/**
 * Sample Usage: FCParameters fcParams = new FCParameters("Column2D.swf",
 * "myFirst", "100", "200", "false", "false", "window", "CCCCCC", "", "EN",
 * null, "", "", "xml", "flash", null);
 * 
 * fcParams.toJSON();
 * 
 * @author InfoSoft Global (P) Ltd.
 * 
 */
public class FCParameters {

	/**
	 * Enum for the parameters to the FusionCharts JS constructor
	 * 
	 * @author InfoSoft Global (P) Ltd.
	 * 
	 */
	enum FCParams {
		SWFURL("swfUrl"), WIDTH("width"), HEIGHT("height"), RENDERAT("renderAt"), RENDERER(
				"renderer"), DATASOURCE("dataSource"), DATAFORMAT("dataFormat"), ID(
				"id"), LANG("lang"), DEBUGMODE("debugMode"), REGISTERWITHJS(
				"registerWithJS"), DETECTFLASHVERSION("detectFlashVersion"), AUTOINSTALLREDIRECT(
				"autoInstallRedirect"), WMODE("wMode"), SCALEMODE("scaleMode"), MENU(
				"menu"), BGCOLOR("bgColor"), QUALITY("quality");

		String paramName = "";

		private FCParams(String paramName) {
			this.paramName = paramName;
		}

		public String getParamName() {
			return paramName;
		}

	}

	/**
	 * Produce a string in double quotes with backslash sequences in all the
	 * right places. In JSON text, a string cannot contain a control character
	 * or an unescaped quote or backslash.
	 * 
	 * @param string
	 *            A String
	 * @return A String correctly formatted for insertion in a JSON text.
	 */
	public static String quote(String string) {
		if (string == null || string.length() == 0) {
			return "\"\"";
		}

		char b;
		char c = 0;
		int i;
		int len = string.length();
		StringBuffer sb = new StringBuffer(len + 4);
		String t;

		sb.append('"');
		for (i = 0; i < len; i += 1) {
			b = c;
			c = string.charAt(i);
			switch (c) {
			case '\\':
			case '"':
				sb.append('\\');
				sb.append(c);
				break;
			/*
			 * case '/': if (b == '<') { sb.append('\\'); } sb.append(c); break;
			 */
			case '\b':
				sb.append("\\b");
				break;
			case '\t':
				sb.append("\\t");
				break;
			case '\n':
				sb.append("\\n");
				break;
			case '\f':
				sb.append("\\f");
				break;
			case '\r':
				sb.append("\\r");
				break;
			default:
				if (c < ' ' || (c >= '\u0080' && c < '\u00a0')
						|| (c >= '\u2000' && c < '\u2100')) {
					t = "000" + Integer.toHexString(c);
					sb.append("\\u" + t.substring(t.length() - 4));
				} else {
					sb.append(c);
				}
			}
		}
		sb.append('"');
		return sb.toString();
	}

	HashMap<FCParams, String> parameters = null;

	/**
	 * Default Constructor
	 */
	public FCParameters() {
		parameters = new HashMap<FCParams, String>();
	}

	/**
	 * Constructor with limited parameters. The mandatory values only.
	 * 
	 * @param swfFilename
	 * @param chartId
	 * @param width
	 * @param height
	 * @param debugMode
	 * @param registerWithJS
	 * @param dataSource
	 * @param dataFormat
	 * @param renderer
	 * @param renderAt
	 */
	public FCParameters(String swfFilename, String chartId, String width,
			String height, String debugMode, String registerWithJS,
			String dataSource, String dataFormat, String renderer,
			String renderAt) {
		super();

		parameters = new HashMap<FCParams, String>();
		addParameterValue(FCParams.ID.toString(), chartId);
		addParameterValue(FCParams.SWFURL.toString(), swfFilename);
		addParameterValue(FCParams.WIDTH.toString(), width);
		addParameterValue(FCParams.HEIGHT.toString(), height);
		addParameterValue(FCParams.DEBUGMODE.toString(), debugMode);
		addParameterValue(FCParams.REGISTERWITHJS.toString(), registerWithJS);
		addParameterValue(FCParams.RENDERER.toString(), renderer);
		addParameterValue(FCParams.RENDERAT.toString(), renderAt);
		addParameterValue(FCParams.DATAFORMAT.toString(), dataFormat);
		addParameterValue(FCParams.DATASOURCE.toString(), dataSource);
	}

	/**
	 * @param swfFilename
	 * @param chartId
	 * @param width
	 * @param height
	 * @param debugMode
	 * @param registerWithJS
	 * @param windowMode
	 * @param bgColor
	 * @param scaleMode
	 * @param lang
	 * @param detectFlashVersion
	 * @param autoInstallRedirect
	 * @param dataSource
	 * @param dataFormat
	 * @param renderer
	 * @param renderAt
	 */
	public FCParameters(String swfFilename, String chartId, String width,
			String height, String debugMode, String registerWithJS,
			String windowMode, String bgColor, String scaleMode, String lang,
			String detectFlashVersion, String autoInstallRedirect,
			String dataSource, String dataFormat, String renderer,
			String renderAt) {
		super();

		parameters = new HashMap<FCParams, String>();
		addParameterValue(FCParams.ID.toString(), chartId);
		addParameterValue(FCParams.SWFURL.toString(), swfFilename);
		addParameterValue(FCParams.WIDTH.toString(), width);
		addParameterValue(FCParams.HEIGHT.toString(), height);
		addParameterValue(FCParams.DEBUGMODE.toString(), debugMode);
		addParameterValue(FCParams.REGISTERWITHJS.toString(), registerWithJS);
		addParameterValue(FCParams.WMODE.toString(), windowMode);
		addParameterValue(FCParams.SCALEMODE.toString(), scaleMode);
		addParameterValue(FCParams.BGCOLOR.toString(), bgColor);
		addParameterValue(FCParams.LANG.toString(), lang);
		addParameterValue(FCParams.AUTOINSTALLREDIRECT.toString(),
				autoInstallRedirect);
		addParameterValue(FCParams.DETECTFLASHVERSION.toString(),
				detectFlashVersion);
		addParameterValue(FCParams.RENDERER.toString(), renderer);
		addParameterValue(FCParams.RENDERAT.toString(), renderAt);
		addParameterValue(FCParams.DATAFORMAT.toString(), dataFormat);
		addParameterValue(FCParams.DATASOURCE.toString(), dataSource);
	}

	/**
	 * @param key
	 * @param value
	 * @return
	 */
	public boolean addParameterValue(String key, String value) {
		// test validity of key
		boolean validKey = testValidity(key);
		if (validKey && value != null) {
			parameters.put(Enum.valueOf(FCParams.class, key), value);
		}
		return validKey;
	}

	/**
	 * @param params
	 * @return
	 */
	public boolean addParameterValues(HashMap<String, String> params) {

		boolean validKey = true;

		Set<String> keySet = params.keySet();
		String key = "";
		String value = "";
		for (Iterator iterator = keySet.iterator(); iterator.hasNext();) {
			key = (String) iterator.next();
			value = params.get(key);
			addParameterValue(key, value);
		}
		return validKey;
	}

	/**
	 * Remove a name and its value, if present.
	 * 
	 * @param key
	 *            The name to be removed.
	 * @return The value that was associated with the name, or null if there was
	 *         no value.
	 */
	public Object remove(String key) {
		return this.parameters.remove(key);
	}

	/**
	 * @param key
	 * @return
	 */
	public boolean testValidity(String key) {
		boolean validParam = true;
		try {
			Enum FCParams = Enum.valueOf(FCParams.class, key);
		} catch (IllegalArgumentException ex) {
			// this is not a valid parameter to FC
			validParam = false;

		}

		return validParam;
	}

	/**
	 * @return
	 */
	public String toJSON() {
		String json_representation = "";
		try {
			Iterator<FCParams> keys = parameters.keySet().iterator();
			StringBuffer sb = new StringBuffer("{");

			while (keys.hasNext()) {
				if (sb.length() > 1) {
					sb.append(',');
				}
				FCParams o = keys.next();
				sb.append(quote(o.getParamName()));
				sb.append(':');
				sb.append(quote(this.parameters.get(o)));
			}
			sb.append('}');
			json_representation = sb.toString();
		} catch (Exception e) {
			return null;
		}

		return json_representation;
	}
}
