package com.fusioncharts.exporter.beans;

/**
 * Parameter names used in export. Currently - exportaction, exportformat,
 * exportfilename and exporttargetwindow.
 * 
 * @author InfoSoft Global (P) Ltd.
 * 
 */
public enum ExportParameterNames {

	EXPORTACTION("exportaction"), EXPORTFORMAT("exportformat"), EXPORTFILENAME(
			"exportfilename"), EXPORTTARGETWINDOW("exporttargetwindow");

	private String paramName;

	private ExportParameterNames(String paramName) {
		this.paramName = paramName;
	}

	@Override
	public String toString() {
		return this.paramName;
	}
}
