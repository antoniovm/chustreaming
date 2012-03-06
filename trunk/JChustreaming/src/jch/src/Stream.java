package jch.src;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.URL;
import java.net.URLConnection;


public class Stream {
	private URL url;
	private HttpURLConnection conexion;
	
	
	public Stream(String url) {
		try {
			//url = new URL("http", "localhost", 8000, "/scordraw.ogg");
			this.url = new URL(url);
			
			
		} catch (MalformedURLException e) {
			
			e.printStackTrace();
		}
		
						
	}
	
	
	/**
	 * Lee el flujo de datos de la respuesta del servidor
	 * @throws IOException
	 */
	public void leerRespuesta() throws IOException {
		String respuesta="", token="";
        BufferedReader br = new BufferedReader(new InputStreamReader(conexion.getInputStream()));
        
        
        try {
			conexion.setRequestMethod("GET");
		} catch (ProtocolException e) {
			
		}
        while ((token = br.readLine()) != null)
        	respuesta +=token;
        
        System.out.println(respuesta);
        br.close();
        


		
		
	}

	/**
	 * Establece conexion con el servidor de la url usada para construir el objeto
	 */
	public boolean establecerConexion() throws IOException{
		if(url==null)
			return false;
		
		conexion = (HttpURLConnection) url.openConnection();	//Abrir conexion
		
		return true;
		
	}
}
	