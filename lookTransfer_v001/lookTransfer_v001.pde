/**
 * LoadFile 1
 * 
 * Loads a text file that contains two numbers separated by a tab ('\t').
 * A new pair of numbers is loaded each frame and used to draw a point on the screen.
 */


PImage sourceChart, destChart;
String sourceChartFile = "wedge_dslr.tga";
String destChartFile = "wedge_instax.tga";

PImage subject;
String subjectFile = "bounceHouse.png";
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

  for (int i=0; i<SRC_CLOUD.length; i++) {
    print(i);
    print(": ");
    print(SRC_CLOUD[i]);
    print(" ");
    println(DEST_CLOUD[i]);
  }
  println("source and destination point clouds loaded.");

  println("setup done.");






  noLoop();
}

PImage lookTransfer(PImage sourceImage) {
  // Look up all the pixels from sourceImage in the sourceChart, and replace 
  // with the corresponding value from destChart. Return the resulting PImage.

  // Small for easier debugging!
  subject.resize(3, 3);
  subject.loadPixels();

  float x, y, z;

  //for (int i=0; i<sourceImage.pixels.length; i++) {
  //  x = red(subject.pixels[i]);
  //  y = green(subject.pixels[i]);
  //  z = blue(subject.pixels[i]);
  //  println(x, y, z);

  //  PVector pixel = new PVector(x, y, z);
  //  Integer indexOfNearestPoint = -1;
  //  Float distanceToNearestPoint = 1000.0;




  //    println(pixel);
  //    PVector distanceVector = pixel;
  //    println(distanceVector);
  //    distanceVector.sub(SRC_CLOUD[j]);
  //    //println(distanceVector, distanceVector.mag());

  //    if (distanceVector.mag() < distanceToNearestPoint) {
  //      indexOfNearestPoint = j;
  //      distanceToNearestPoint = distanceVector.mag();
  //      //println(indexOfNearestPoint, distanceToNearestPoint);
  //    }


  return(sourceImage);
}


void draw() {

  subject = loadImage(subjectFile); 

  PImage result = lookTransfer(subject);
  image(result, 0, 0, 100, 100);
}