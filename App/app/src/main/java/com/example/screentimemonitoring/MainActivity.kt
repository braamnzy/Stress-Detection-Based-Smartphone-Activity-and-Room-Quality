package com.example.screentimemonitoring

import android.app.usage.UsageStats
import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.Settings
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.work.*
import java.util.concurrent.TimeUnit
import java.util.Calendar
import android.Manifest
import android.content.pm.PackageManager
import android.app.AlertDialog
import android.widget.EditText
import android.text.InputType


class MainActivity : AppCompatActivity() {

    private lateinit var tvResult: TextView
    private lateinit var btnRequestPermission: Button
    private lateinit var btnGetUsage: Button
    private lateinit var btnChangeIp: Button
    private val NOTIFICATION_PERMISSION_CODE = 101
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        tvResult = findViewById(R.id.tvResult)
        btnRequestPermission = findViewById(R.id.btnRequestPermission)
        btnGetUsage = findViewById(R.id.btnUsage)
        btnChangeIp = findViewById(R.id.btnChangeIp)
        setupChangeIpButton()
        requestNotificationPermission()
        btnRequestPermission.setOnClickListener {
            requestUsageAccess()
        }
        if (!isIgnoringBatteryOptimizations()) {
            requestDisableBatteryOptimization()
        }
        btnGetUsage.setOnClickListener {
            if (hasUsageAccess()) {
                showUsageStats()
                schedulePeriodicMonitoring()
                showLastStressStatus()
            } else {
                tvResult.text = "Akses belum diizinkan!"
            }
        }

        if (hasUsageAccess()) {
            schedulePeriodicMonitoring()
        }
    }
    private fun setupChangeIpButton() {
        btnChangeIp.setOnClickListener {
            showIpInputDialog()
        }
    }
    private fun showIpInputDialog() {
        val builder = AlertDialog.Builder(this)
        builder.setTitle("Ubah Alamat Server Flask")

        val input = EditText(this)
        input.hint = "cth: http://192.168.1.105:5000"
        input.setText(ServerConfig.BASE_URL)
        input.inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS
        builder.setView(input)

        builder.setPositiveButton("Simpan") { dialog, which ->
            val newUrl = input.text.toString().trim()
            if (newUrl.startsWith("http://", ignoreCase = true)) {
                ServerConfig.BASE_URL = newUrl
                tvResult.text = "✅ IP Server Diperbarui ke:\n$newUrl"
                schedulePeriodicMonitoring()
            } else {
                tvResult.text = "❌ Format URL tidak valid (harus diawali http://)"
            }
        }
        builder.setNegativeButton("Batal") { dialog, which -> dialog.cancel() }

        builder.show()
    }
    private fun isIgnoringBatteryOptimizations(): Boolean {
        val pm = getSystemService(Context.POWER_SERVICE) as android.os.PowerManager
        return pm.isIgnoringBatteryOptimizations(packageName)
    }
    private fun requestDisableBatteryOptimization() {
        val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
        intent.data = Uri.parse("package:$packageName")
        startActivity(intent)
    }
    private fun showLastStressStatus() {
        val prefs = getSharedPreferences("stress_prefs", Context.MODE_PRIVATE)
        val message = prefs.getString(
            "last_stress_message",
            "Belum ada analisis stres."
        )

        tvResult.append("\n\n🧠 Status Stres Terakhir:\n$message")
    }
    private fun requestNotificationPermission() {
        // Cek jika versi Android adalah TIRAMISU (API 33) atau lebih tinggi
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {

            // Periksa apakah izin sudah diberikan
            if (ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                // Minta izin notifikasi secara eksplisit
                ActivityCompat.requestPermissions(
                    this,
                    arrayOf(Manifest.permission.POST_NOTIFICATIONS),
                    NOTIFICATION_PERMISSION_CODE
                )
            }
        }
    }
    private fun hasUsageAccess(): Boolean {
        // ... (Fungsi ini tetap sama)
        val appOps = getSystemService(Context.APP_OPS_SERVICE) as android.app.AppOpsManager
        val mode = appOps.checkOpNoThrow(
            android.app.AppOpsManager.OPSTR_GET_USAGE_STATS,
            android.os.Process.myUid(),
            packageName
        )
        return mode == android.app.AppOpsManager.MODE_ALLOWED
    }
    private fun requestUsageAccess() {
        startActivity(Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS))
    }
    private fun showUsageStats() {
        tvResult.text = """
            Monitoring aktif.
            Data penggunaan layar dihitung otomatis di background
            dan dikirim ke server setiap 15 menit.
        """.trimIndent()
    }


    private fun schedulePeriodicMonitoring() {
        val workManager = WorkManager.getInstance(applicationContext)
        val tag = "UsageMonitorTag"

        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        // Interval: 15 Menit (900.000 ms)
        // Flex: 5 Menit (WorkManager akan mencoba berjalan antara menit ke-10 hingga menit ke-15)
        val periodicWorkRequest = PeriodicWorkRequestBuilder<UsageDataWorker>(
            15, TimeUnit.MINUTES,    // Jeda Total
            5, TimeUnit.MINUTES     // Jendela Fleksibel (Minimal 5 Menit)
        )
            .setConstraints(constraints)
            .addTag(tag)
            .build()

        workManager.enqueueUniquePeriodicWork(
            tag,
            ExistingPeriodicWorkPolicy.REPLACE,
            periodicWorkRequest
        )
    }
}