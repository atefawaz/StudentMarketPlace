package com.epita.marketplace;

import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;

/**
 * Create item form.
 *
 * TODO: Read values from the form fields.
 * TODO: Validate that title, price, category, and seller name are not empty.
 * TODO: POST the new item to /items using ApiClient.post().
 * TODO: On success, finish() to return to the list. On error, show a Toast.
 */
public class CreateItemActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_create_item);

        // TODO: Wire up the submit button to collect form data and POST it
    }
}
