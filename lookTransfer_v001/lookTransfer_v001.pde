/**
 What a mess.
 */


PImage sourceChart, destChart;
String sourceChartFile = "wedge_dslr.tga";
String destChartFile = "wedge_instax.tga";

PImage subject;
String subjectFile = "jessicaPainting.png";
PVector[] SRC_CLOUD;
PVector[] DEST_CLOUD;

int index = 0;

void setup() {
  size(200, 200);
  background(0);
  stroke(255);
  frameRate(12);
  colorMode(RGB, 255);

  sourceChart = loadImage(sourceChartFile);
  destChart = loadImage(destChartFile);

  // load source and destination pixel values for later lookup
  Float x, y, z;
  sourceChart.loadPixels();
  SRC_CLOUD = new PVector[sourceChart.pixels.length];
  for ( int i=0; i<sourceChart.pixels.length; i++) {
    x = red(sourceChart.pixels[i]);
    y = green(sourceChart.pixels[i]);
    z = blue(sourceChart.pixels[i]);
    //println( x, y, z);
    SRC_CLOUD[i] = new PVector(x, y, z);
  }

  destChart.loadPixels();
  DEST_CLOUD = new PVector[destChart.pixels.length];
  for ( int i=0; i<destChart.pixels.length; i++) {
    x = red(destChart.pixels[i]);
    y = green(destChart.pixels[i]);
    z = blue(destChart.pixels[i]);
    //println( x, y, z);
    DEST_CLOUD[i] = new PVector(x, y, z);
  }

  //for (int i=0; i<SRC_CLOUD.length; i++) {
  //  print(i);
  //  print(": ");
  //  print(SRC_CLOUD[i]);
  //  print(" ");
  //  println(DEST_CLOUD[i]);
  //}
  println("source and destination point clouds loaded.");

  println("setup done.");

  noLoop();
}

PImage lookTransfer(PImage sourceImage) {
  // Look up all the pixels from sourceImage in the sourceChart, and replace 
  // with the corresponding value from destChart. Return the resulting PImage.

  // Small for easier debugging!
  //subject.resize(5, 5);
  subject.loadPixels();

  PImage destImage = sourceImage;
  destImage.loadPixels();

  for (int i=0; i<sourceImage.pixels.length; i++) {
    destImage.pixels[i] = sourceColorToDestColor(sourceImage.pixels[i]);
  }
  destImage.updatePixels();

  return destImage;
}

color sourceColorToDestColor(color sourceColor) {

  float x, y, z;
  x = red(sourceColor);
  y = green(sourceColor);
  z = blue(sourceColor);
  PVector source = new PVector(x, y, z);
  PVector dest = new PVector(-1.0, -1.0, -1.0);

  FloatDict distanceMap = new FloatDict();
  for (int i=0; i<SRC_CLOUD.length; i++) {
    distanceMap.set(str(i), source.dist(SRC_CLOUD[i]));
  }
  distanceMap.sortValues();
  //println(distanceMap);
  //print("closest: ");
  //print(distanceMap.keyArray()[0]);
  //println(SRC_CLOUD[int(distanceMap.keyArray()[0])]);
  //print("second closest: ");
  //print(distanceMap.keyArray()[1]);
  //println(SRC_CLOUD[int(distanceMap.keyArray()[1])]);


  color closestColor = color(DEST_CLOUD[int(distanceMap.keyArray()[0])].x,
                             DEST_CLOUD[int(distanceMap.keyArray()[0])].y,
                             DEST_CLOUD[int(distanceMap.keyArray()[0])].z);
  color nextClosest = color(DEST_CLOUD[int(distanceMap.keyArray()[0])].x,
                            DEST_CLOUD[int(distanceMap.keyArray()[0])].y,
                            DEST_CLOUD[int(distanceMap.keyArray()[0])].z);
                            
  float factor = distanceMap.valueArray()[0]

  dest = lerpColor(closestColor, nextClosest, factor);
  color destColor = color(dest.x, dest.y, dest.z);
  return destColor;
}


void draw() {

  color dest = sourceColorToDestColor(color(180, 60, 60));
  print("nearest color: ");
  print(red(dest));
  print(", ");
  print(green(dest));
  print(", ");
  print(blue(dest));
  println();

  //subject = loadImage(subjectFile); 
  //image(subject, 0, 0, 100, 100);
  //PImage result = lookTransfer(subject);
  //image(result, 100, 0, 100, 100);
}