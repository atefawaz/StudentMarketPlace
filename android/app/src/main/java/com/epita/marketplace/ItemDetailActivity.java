package com.epita.marketplace;

import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;

/**
 * Item detail screen.
 *
 * TODO: Load item data from GET /items/{id} and populate the layout.
 * TODO: Display all item fields (title, description, price, category, seller, date).
 * TODO: If the item is sold, show a "SOLD" badge.
 * TODO: Add a "Mark as sold" button that calls PATCH /items/{id}.
 */
public class ItemDetailActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_item_detail);

        int itemId = getIntent().getIntExtra("item_id", -1);

        // TODO: Fetch item details from the API and bind to views
    }
}
