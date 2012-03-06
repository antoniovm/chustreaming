package jch.src;

import java.io.IOException;

public class Princi {
	static Stream stream;
	public static void main(String[] args) throws IOException {
		stream = new Stream("http://www.google.com");
		stream.establecerConexion();
		stream.leerRespuesta();
	}
}
