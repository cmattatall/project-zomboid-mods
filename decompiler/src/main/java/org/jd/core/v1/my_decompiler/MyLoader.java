package org.jd.core.v1.my_decompiler;

import org.jd.core.v1.api.loader.Loader;
import java.io.InputStream;
import org.jd.core.v1.api.loader.LoaderException;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileInputStream;

public class MyLoader implements Loader {

    public byte[] load(String internalName) throws LoaderException {
        // System.out.println("TRYING TO LOAD: " + internalName); //debug
        File f = new File(internalName);
        InputStream is = null;
        try {
            is = new FileInputStream(f);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }

        if (is == null) {
            return null;
        } else {
            try (InputStream in = is;
                    ByteArrayOutputStream out = new ByteArrayOutputStream()) {
                byte[] buffer = new byte[1024];
                int read = in.read(buffer);

                while (read > 0) {
                    out.write(buffer, 0, read);
                    read = in.read(buffer);
                }

                return out.toByteArray();
            } catch (IOException e) {
                throw new LoaderException(e);
            }
        }
    }

    @Override
    public boolean canLoad(String internalName) {
        // System.out.println("CHECKING IF CAN LOAD: " + internalName); //debug
        return new File(internalName).exists();
    }
}