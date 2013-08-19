package com.fusioncharts.sampledata;

/**
 * Bean containing sample chart data. Default values for all the fields have
 * been set. These can be changed using the set methods. This class has been
 * used as a backing bean in JSF examples.
 * 
 * @author Infosoft Global (P) Ltd.
 * 
 */
public class BasicRenderData {

	protected String xml;
	protected String chartId = "basicChart";
	protected String url = "Data/Data.xml";
	protected String jsonUrl = "Data/Data.json";
	protected String width = "600";
	protected String height = "300";
	protected String swfFilename = ChartType.COLUMN3D.getFileName();
	protected String uniqueId = "";

	public BasicRenderData() {
		xml = "<chart caption='Monthly Unit Sales' xAxisName='Month' yAxisName='Units' showValues='0' formatNumberScale='0' showBorder='1'>";
		xml += "<set label='Jan' value='462' />";
		xml += "<set label='Feb' value='857' />";
		xml += "<set label='Mar' value='671' />";
		xml += "<set label='Apr' value='494' />";
		xml += "<set label='May' value='761' />";
		xml += "<set label='Jun' value='960' />";
		xml += "<set label='Jul' value='629' />";
		xml += "<set label='Aug' value='622' />";
		xml += "<set label='Sep' value='376' />";
		xml += "<set label='Oct' value='494' />";
		xml += "<set label='Nov' value='761' />";
		xml += "<set label='Dec' value='960' />";
		xml += "</chart>";
	}

	public String getChartId() {
		return chartId;
	}

	public String getHeight() {
		return height;
	}

	/**
	 * @return the jsonUrl
	 */
	public String getJsonUrl() {
		return jsonUrl;
	}

	/**
	 * @return the swfFilename
	 */
	public String getSwfFilename() {
		return swfFilename;
	}

	/**
	 * @return the uniqueId
	 */
	public String getUniqueId() {
		int randomNum = (int) Math.floor(Math.random() * 100);
		uniqueId = "Chart" + "_" + randomNum;
		return uniqueId;
	}

	public String getUrl() {
		return url;
	}

	public String getWidth() {
		return width;
	}

	public String getXml() {
		return xml;
	}

	public void setChartId(String chartId) {
		this.chartId = chartId;
	}

	public void setHeight(String height) {
		this.height = height;
	}

	/**
	 * @param jsonUrl
	 *            the jsonUrl to set
	 */
	public void setJsonUrl(String jsonUrl) {
		this.jsonUrl = jsonUrl;
	}

	/**
	 * @param swfFilename
	 *            the swfFilename to set
	 */
	public void setSwfFilename(String swfFilename) {
		this.swfFilename = swfFilename;
	}

	/**
	 * @param uniqueId
	 *            the uniqueId to set
	 */
	public void setUniqueId(String uniqueId) {
		this.uniqueId = uniqueId;
	}

	public void setUrl(String url) {
		this.url = url;
	}

	public void setWidth(String width) {
		this.width = width;
	}

	public void setXml(String xml) {
		this.xml = xml;
	}
}
