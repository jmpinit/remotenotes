package com.example.remotenotes;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v7.app.ActionBarActivity;
import android.support.v7.app.ActionBar;
import android.support.v4.app.Fragment;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.os.Build;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;

public class OverviewActivity extends ActionBarActivity {
    static final int REQUEST_IMAGE_CAPTURE = 1;

    ImageView mImageView;
    EditText txtAddress;

    private Bitmap bitmap;
    private ImageView imageView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_overview);

        mImageView = (ImageView)findViewById(R.id.img_thumbnail);
        txtAddress = (EditText)findViewById(R.id.txt_address);
    }

    public void onButtonClick(View v) {
        Intent intent = new Intent();
        intent.setType("image/*");
        intent.setAction(Intent.ACTION_GET_CONTENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        startActivityForResult(intent, REQUEST_IMAGE_CAPTURE);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        InputStream stream = null;

        if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == Activity.RESULT_OK) {
            try {
                // recycle unused bitmaps
                if (bitmap != null) {
                    bitmap.recycle();
                }

                stream = getContentResolver().openInputStream(data.getData());
                ByteArrayOutputStream picSourceStream = new ByteArrayOutputStream();

                InputStream picViewStream = null;
                InputStream picUploadStream = null;
                try {
                    byte[] buffer = new byte[1024];

                    int len;
                    while ((len = stream.read(buffer)) > -1) {
                        picSourceStream.write(buffer, 0, len);
                    }
                    picSourceStream.flush();

                    picViewStream = new ByteArrayInputStream(picSourceStream.toByteArray());
                    picUploadStream = new ByteArrayInputStream(picSourceStream.toByteArray());
                } catch(IOException ex) {
                    Log.e("Remote Notes", ex.toString());

                    StringWriter sw = new StringWriter();
                    PrintWriter pw = new PrintWriter(sw);
                    ex.printStackTrace(pw);

                    Log.e("Remote Notes", sw.toString());
                }

                // display the image
                bitmap = BitmapFactory.decodeStream(stream);
                mImageView.setImageBitmap(bitmap);

                if(picUploadStream != null) {
                    uploadFile(picSourceStream.toByteArray(), "http://" + txtAddress.getText() + "/analyze");
                } else {
                    Context context = getApplicationContext();
                    CharSequence text = "can't upload - null stream";
                    int duration = Toast.LENGTH_SHORT;

                    Toast toast = Toast.makeText(context, text, duration);
                    toast.show();
                }
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            } finally {
                if (stream != null) {
                    try {
                        stream.close();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }
        }
    }

    void uploadFile(byte[] file, String server) {
        HttpURLConnection connection = null;
        DataOutputStream outputStream = null;
        DataInputStream inputStream = null;

        int bytesRead, bytesAvailable, bufferSize;
        byte[] buffer;
        int maxBufferSize = 1*1024*1024;

        try {
            URL url = new URL(server);
            connection = (HttpURLConnection) url.openConnection();

            // Allow Inputs & Outputs
            connection.setDoInput(true);
            connection.setDoOutput(true);
            connection.setUseCaches(false);

            // enable POST method
            connection.setRequestMethod("POST");

            connection.setRequestProperty("User-Agent", "remote notes");
            connection.setRequestProperty("Accept", "*/*");
            connection.setRequestProperty("Content-Length", "" + file.length);
            connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
            connection.setRequestProperty("Expect", "100-continue");

            outputStream = new DataOutputStream(connection.getOutputStream());

            outputStream.write(file, 0, file.length);

            outputStream.flush();
            outputStream.close();
        } catch (Exception ex) {
            Log.e("Remote Notes", ex.toString());

            StringWriter sw = new StringWriter();
            PrintWriter pw = new PrintWriter(sw);
            ex.printStackTrace(pw);

            Log.e("Remote Notes", sw.toString());
        }
    }
}

